from scrapy import cmdline
from Qiancheng.settings import ip_pool

ip_pool.start()

cmdline.execute(['scrapy', 'crawl', 'qcwy'])
