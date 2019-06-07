# -*- coding: utf-8 -*-
import base64
import random

import scrapy
from scrapy import Request, Selector
from scrapy.http import HtmlResponse

from Qiancheng import QianchengItem
from functools import partial
import re
from Qiancheng.settings import USER_AGENT_POOL
from scrapy_redis.spiders import RedisSpider


def extract_info(response, xp):
    return response.xpath(xp).extract()


class QcwySpider(RedisSpider):
    name = 'qcwy'
    # allowed_domains = ['51job.com']
    redis_key = 'qcwy:start_url'
    BASE_URL = [
        "https://search.51job.com/list/030200%252C020000%252C010000%252C040000%252C180200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=",
        'https://search.51job.com/list/180200%252C200200%252C080200%252C070200%252C090200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/060000%252C030800%252C230300%252C230200%252C070300,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/250200%252C190200%252C150200%252C080300%252C170200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/050000%252C120300%252C120200%252C220200%252C240200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/110200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=01&from=&welfare=',
        'https://search.51job.com/list/030000%252C070000%252C080000%252C090000%252C100000,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/110000%252C120000%252C130000%252C140000%252C150000,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/160000%252C170000%252C180000%252C190000%252C200000,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/210000%252C220000%252C230000%252C240000%252C250000,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
        'https://search.51job.com/list/260000%252C270000%252C280000%252C290000%252C300000,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=', ]
    COMMON_HEADER = {
        "User-Agent": random.choice(USER_AGENT_POOL),
        "Referer": "https://www.51job.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    regSpace = re.compile(r'([\s\r\n\t])+')

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        self.allowed_domains = ['51job.com']

        # 修改这里的类名为当前类名
        super(QcwySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.BASE_URL:
            for i in range(1, 2000):
                yield Request(
                    url=url.format(page=str(i)),
                    headers=self.COMMON_HEADER,
                    callback=self.parse_item,
					dont_filter=True
                )

    def parse_item(self, response):
        for signal_item in response.xpath('//div[@class="el"]')[4:]:  # type:Selector
            _extract_info = partial(extract_info, signal_item)
            item = QianchengItem()
            item['link'] = _extract_info("./p/span/a/@href")[0]
            item['post_time'] = _extract_info('./span[@class="t5"]/text()')[0]
            item['job_name'] = self.replace_all_n(_extract_info('./p/span/a/text()')[0])
            item['salary'] = _extract_info('./span[@class="t4"]/text()')
            item['place'] = _extract_info('./span[@class="t3"]/text()')
            item['company_name'] = _extract_info('./span[@class="t2"]/a/text()')[0]
            item['id'] = base64.b32encode((item['job_name'] + item['company_name']).encode("utf-8")).decode("utf-8")
            self.COMMON_HEADER['Referer'] = response.url
            yield Request(
                url=item['link'],
                headers=self.COMMON_HEADER,
                callback=self.parse_other,
                meta={"item": item}
            )

    def parse_other(self, response: HtmlResponse):
        item = response.meta['item']
        _extract_info = partial(extract_info, response)
        info_text = _extract_info("//p[@class='msg ltype']/@title")[0].split("|") if len(
            _extract_info("//p[@class='msg ltype']/@title")) != 0 else ["空"] * 5
        item['experience'] = info_text[1]
        item['education'] = info_text[2] if len(info_text) == 5 else "空"
        item['job_number'] = info_text[3] if len(info_text) == 5 else info_text[2]
        item['advantage'] = _extract_info('//div[@class="jtag"]/div//span/text()')
        info = _extract_info("//div[@class='com_tag']/p/@title")
        item['company_nature'] = info[0] if len(info) != 0 else "空"
        item['company_size'] = info[1] if len(info) != 0 else "空"
        item['company_industry'] = info[2] if len(info) != 0 else "空"
        item['company_address'] = self.replace_all_n(
            "".join(_extract_info(u"//*[text()='联系方式']/parent::*/parent::*//p/text()")))
        info2 = self.replace_all_n(
            "".join(_extract_info(u"//*[text()='职位信息']/parent::*/parent::*/div//p//text()")))
        loc_div = info2.find(u"职能类别")
        item['job_content'] = info2[:loc_div]
        item['job_kind'] = info2[loc_div:]
        yield item

    def replace_all_n(self, text):
        # 以防止提取不到
        try:
            rel = re.sub(self.regSpace, "", text)
            return rel
        except TypeError as e:
            return "空"
