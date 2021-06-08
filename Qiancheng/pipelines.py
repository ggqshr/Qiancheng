# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from .settings import REDIS_PORT, REDIS_HOST, MODE, MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PASSWORD
import redis as r
from datetime import datetime
from redisbloom.client import Client

LOCAL = "127.0.0.1"


class QianchengPipeline(object):
    def __init__(self):
        self.client = Client(host=REDIS_HOST,port=REDIS_PORT,password="b7310")
        if not self.client.exists("bf:qc"):
            self.client.bfCreate("bf:qc",0.00001,100000)
        self.conn = MongoClient(MONGODB_HOST, MONGODB_PORT)
        self.conn.admin.authenticate(MONGODB_USER, MONGODB_PASSWORD)
        self.mongo = self.conn.QianCheng.QianCheng
        self.count = 0
        self.fcount = 0
        pass

    def process_item(self, item, spider):
        self.count += 1
        if self.client.bfAdd("bf:qc", item['id']) == 0:
            return item
        self.mongo.insert_one(dict(item))
        self.fcount += 1
        return item

    def close_spider(self, spider):
        with open("result.log", "a") as f:
            f.writelines("{} crawl item {} {}\n".format(datetime.now().strftime("%Y.%m.%d"),self.count,self.fcount))
            f.flush()
