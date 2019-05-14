# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QianchengItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()  # 由工作名+公司名 生成的base32编码
    link = scrapy.Field()  # //div[@class="el"]/p/span/a/@href
    post_time = scrapy.Field()  # //div[@class="el"]/span[@class="t5"]/text()
    job_name = scrapy.Field()  # //div[@class="el"]/p/span/a/text()
    salary = scrapy.Field()  # //div[@class="el"]/span[@class="t4"]/text()
    place = scrapy.Field()  # //div[@class="el"]/span[@class="t3"]/text()
    company_name = scrapy.Field()  # //div[@class="el"]/span[@class="t2"]/a/text()
    # 深一层页面
    education = scrapy.Field()  # //p[@class='msg ltype']/@title 按照|分割，第三个字段
    experience = scrapy.Field()  # //p[@class='msg ltype']/@title 按照|分割，第二个字段
    job_number = scrapy.Field() # //p[@class='msg ltype']/@title 按照|分割，第四个字段
    advantage = scrapy.Field()  # //div[@class="jtag"]/div//span/text()
    company_nature = scrapy.Field()  # //div[@class='com_tag']/p/@title 第一项
    company_size = scrapy.Field()  # //div[@class='com_tag']/p/@title 第二项
    company_industry = scrapy.Field()  # //div[@class='com_tag']/p/@title 第三项
    company_address = scrapy.Field()  # //*[text()='联系方式']/parent::*/parent::*//p/text() 可能没有
    job_content = scrapy.Field()  # //*[text()='职位信息']/parent::*/parent::*/div//p//text() 到职能类别之前的信息
    job_kind = scrapy.Field()  # //*[text()='职位信息']/parent::*/parent::*/div//p//text() 职能类别之后的信息
