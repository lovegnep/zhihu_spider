# -*- coding: utf-8 -*-

# Scrapy settings for zhihu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'zhihu'

SPIDER_MODULES = ['zhihu.spiders']
NEWSPIDER_MODULE = 'zhihu.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.87 Safari/537.36'

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
  'Accept-Encoding': 'gzip, deflate, sdch',
  'Connection': 'keep-alive'
}

# 广度优先
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# 项目路径
PROJECT_DIR = os.path.dirname(os.path.abspath(os.path.curdir))

# mongodb配置
MONGO_URI = 'mongodb://127.0.0.1:27017'

DOWNLOADER_MIDDLEWARES = {
    'zhihu.middlewares.monitor': 100,
    #'zhihu.middlewares.JobboleProxyMiddleware' : 125,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'zhihu.middlewares.RotateUserAgentMiddleware' : 400,
    'zhihu.middlewares.respd' : 1000,
}

# pipeline设置
ITEM_PIPELINES = {
    'zhihu.pipelines.ZhihuPipeline': 500,
}

# 异步任务队列
BROKER_URL = 'amqp://lovegnep:liuyang15@127.0.0.1:5672//'

DOWNLOAD_HANDLERS = {
        'S3':None,
}

LOG_FILE = "mySpider.log"

FEED_EXPORT_ENCODING = 'utf-8'

RANDOMIZE_DOWNLOAD_DELAY=False
#DOWNLOAD_DELAY=3
#CONCURRENT_REQUESTS_PER_IP=40
DOWNLOAD_TIMEOUT = 60
RETRY_ENABLED = False