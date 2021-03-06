# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from .settings import REDIS_PORT, REDIS_HOST, MODE, MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PASSWORD
import redis as r
from datetime import datetime

LOCAL = "127.0.0.1"


class QianchengPipeline(object):
    def __init__(self):
        self.client = r.Redis(REDIS_HOST if MODE == 'LOCAL' else LOCAL, port=REDIS_PORT, port=REDIS_PORT)
        self.conn = MongoClient(MONGODB_HOST if MODE == 'LOCAL' else LOCAL, MONGODB_PORT, MONGODB_PORT)
        self.conn.admin.authenticate(MONGODB_USER, MONGODB_PASSWORD)
        self.mongo = self.conn.QianCheng.QianCheng
        self.count = 0
        self.fcount = 0
        pass

    def process_item(self, item, spider):
        self.count += 1
        if self.client.sadd("qianchen_id_set", item['id']) == 0:
            return item
        self.mongo.insert_one(dict(item))
        self.fcount += 1
        return item

    def close_spider(self, spider):
        with open("result.log", "a") as f:
            f.writelines("{} crawl item {} {}\n".format(datetime.now().strftime("%Y.%m.%d"),self.count,self.fcount))
            f.flush()
