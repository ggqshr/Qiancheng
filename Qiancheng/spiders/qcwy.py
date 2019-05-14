# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, Selector
from Qiancheng import QianchengItem
from functools import partial
import re


def extract_info(response, xp):
    return response.xpath(xp).extract()


class QcwySpider(scrapy.Spider):
    name = 'qcwy'
    allowed_domains = ['51job.com']
    BASE_URL = "https://search.51job.com/list/030200%252C020000%252C010000%252C040000%252C180200,000000,0000,00,0,99,%2B,2,{page}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=5&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
    COMMON_HEADER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        "Referer": "https://www.51job.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    regSpace = re.compile(r'([\s\r\n\t])+')

    def start_requests(self):
        for i in range(1, 2000):
            yield Request(
                url=self.BASE_URL.format(page=str(i)),
                headers=self.COMMON_HEADER,
                callback=self.parse
            )

    def parse(self, response):
        for signal_item in response.xpath('//div[@class="el"]')[4:]:  # type:Selector
            _extract_info = partial(extract_info, signal_item)
            item = QianchengItem()
            item['link'] = _extract_info("./p/span/a/@href")[0]
            item['post_time'] = _extract_info('./span[@class="t5"]/text()')[0]
            item['job_name'] = self.replace_all_n(_extract_info('./p/span/a/text()')[0])
            item['salary'] = _extract_info('./span[@class="t4"]/text()')
            item['place'] = _extract_info('./span[@class="t3"]/text()')
            item['company_name'] = _extract_info('./span[@class="t2"]/a/text()')
            self.COMMON_HEADER['Referer'] = response.url
            yield Request(
                url=item['link'],
                headers=self.COMMON_HEADER,
                callback=partial(self.parse_other, item)
            )

    def parse_other(self, item, response):
        _extract_info = partial(extract_info, response)
        info_text = _extract_info("//p[@class='msg ltype']/@title")[0].split("|") if len(
            _extract_info("//p[@class='msg ltype']/@title")) != 0 else ["空"] * 5
        item['experience'] = info_text[1]
        item['education'] = info_text[2] if len(info_text) == 5 else "空"
        item['job_number'] = info_text[3] if len(info_text) == 5 else info_text[2]
        item['advantage'] = _extract_info('//div[@class="jtag"]/div//span/text()')
        info = _extract_info("//div[@class='com_tag']/p/@title")
        item['company_nature'] = info[0]
        item['company_size'] = info[1]
        item['company_industry'] = info[2]
        item['company_address'] = self.replace_all_n(
            "".join(_extract_info(u"//*[text()='联系方式']/parent::*/parent::*//p/text()")))
        info2 = self.replace_all_n("".join(_extract_info(u"//*[text()='职位信息']/parent::*/parent::*/div//p//text()")))
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
