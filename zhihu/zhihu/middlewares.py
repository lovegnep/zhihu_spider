
import logging
import codecs
import datetime
import random
# 导入官方文档对应的HttpProxyMiddleware
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
from zhihu.client.py_cli import ProxyFetcher

logger=logging.getLogger()

class monitor(object):
    def process_request(self, request, spider):
        logger.info('monitor process_request:%s', request.url)

    def process_response(self, request, response, spider):
        logger.info('monitor process_response:%d',response.status)
        return response

    def process_exception(self, request, exception, spider):
        logger.info('monitor process_exception:%s',  request.url)
        return request

class IPPOOlS(HttpProxyMiddleware):

    def process_request(self, request, spider):
        args = dict(host='127.0.0.1', port=6379, password='123456', db=0)
        fetcher = ProxyFetcher('zhihu', strategy='greedy', redis_args=args)
        #thisiparr = fetcher.get_proxies()
        #thisip = random.choice(thisiparr)
        thisip = fetcher.get_proxy()
        logger.info("当前使用proxy是："+ thisip)
        request.meta["proxy"] = thisip


class respd(object):

    def process_response(self, request, response, spider):
        logger.info('respd process_response:%d',response.status)
        return response

    def process_exception(self, request, exception, spider):
        logger.info('respd process_exception:%s',  request.url)
        return request