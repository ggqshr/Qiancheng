# -*- coding: utf-8 -*-
import base64
import random
import re
from datetime import datetime
from functools import partial
import json

import scrapy
from itemloaders.processors import Compose, Join, MapCompose, SelectJmes, TakeFirst
from Qiancheng import QianchengItem, QianchengItemLoader
from Qiancheng.settings import USER_AGENT_POOL, city_list_id_dict
from scrapy import Request, Selector
from scrapy.http import HtmlResponse
from scrapy_redis.spiders import RedisSpider


def extract_info(response, xp):
    return response.xpath(xp).extract()


class QcwySpider(scrapy.Spider):
    name = 'qcwy'
    # allowed_domains = ['51job.com']
    BASE_URL = "https://search.51job.com/list/{city},000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
    COMMON_HEADER = {
        "User-Agent": random.choice(USER_AGENT_POOL),
        "Referer": "https://www.51job.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    regSpace = re.compile(r'([\s\r\n\t])+')
    date_year = datetime.now().strftime("%Y-")

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        self.allowed_domains = ['51job.com']

        # 修改这里的类名为当前类名
        super(QcwySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        city_id_list = set(city_list_id_dict.values())
        for city in city_id_list:
            yield Request(
                url=self.BASE_URL.format(page=str(1), city=str(city)),
                headers=self.COMMON_HEADER,
                callback=self.loop_on_page,
                dont_filter=True,
                meta={"city": city}
            )

    def loop_on_page(self, response):
        """
        根据页数循环
        :param response:
        :return:
        """
        this_city = response.meta['city']
        loader = QianchengItemLoader()
        info = json.loads(loader.get_value(response.text,TakeFirst(),re='window.__SEARCH_RESULT__\s*=\s*(.*?)\<\/script\>'))
        all_pages = info['total_page']
        for page in range(1, int(all_pages) + 1):
            yield Request(
                url=self.BASE_URL.format(page=str(page), city=this_city),
                headers=self.COMMON_HEADER,
                callback=self.parse_item,
                dont_filter=True,
                priority=3,
            )

    def parse_item(self, response):
        loader = QianchengItemLoader()
        infos = json.loads(loader.get_value(response.text,TakeFirst(),re='window.__SEARCH_RESULT__\s*=\s*(.*?)\<\/script\>'))
        all_position = infos['engine_search_result']
        for position in all_position:  # type:Selector
            this_loader = QianchengItemLoader(QianchengItem())
            this_loader.add_value(
                None,
                {
                    "link":position,
                    "post_time":position,
                    "job_name":position,
                    "salary":position,
                    "place":position,
                    "company_name":position,
                }
            )
            this_id = base64.b32encode((this_loader.get_output_value('job_name') + this_loader.get_output_value('company_name')).encode("utf-8")).decode("utf-8")
            this_loader.add_value("id",this_id)
            self.COMMON_HEADER['Referer'] = response.url
            item = this_loader.load_item()
            yield Request(
                url=item['link'],
                headers=self.COMMON_HEADER,
                callback=self.parse_other,
                meta={"item": item},
                priority=3,
            )

    def parse_other(self, response: HtmlResponse):
        item = response.meta['item']
        loader = QianchengItemLoader(item,response)
        _extract_info = partial(extract_info, response)
        info_text = _extract_info("//p[@class='msg ltype']/@title")[0].split("|") if len(
            _extract_info("//p[@class='msg ltype']/@title")) != 0 else ["空"] * 5
        loader.add_value("experience",info_text[1])
        loader.add_value("education",info_text[2] if len(info_text) == 5 else "空")
        loader.add_value("job_number",info_text[3] if len(info_text) == 5 else info_text[2])
        loader.add_xpath("advantage",'//div[@class="jtag"]/div//span/text()',processors=Compose(Join()))

        info = _extract_info("//div[@class='com_tag']/p/@title")

        loader.add_value("company_nature",info[0] if len(info) != 0 else "空")
        loader.add_value("company_size",info[1] if len(info) != 0 else "空")
        loader.add_value("company_industry",info[2] if len(info) != 0 else "空")
        loader.add_xpath("company_address","//*[text()='联系方式']/parent::*/parent::*//p/text()",processors=Compose(Join(""),self.replace_all_n))

        info2 = self.replace_all_n(
            "".join(_extract_info(u"//*[text()='职位信息']/parent::*/parent::*/div//p//text()")))
        loc_div = info2.find(u"职能类别")

        loader.add_value("job_content",info2[:loc_div])
        loader.add_value("job_kind",info2[loc_div:])
        yield loader.load_item()

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            rel = re.sub(self.regSpace, "", text)
            return rel
        except TypeError as e:
            return "空"
