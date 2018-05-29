
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

    def _faillog(self, request, errorType, reason, spider):
        with codecs.open('log/faillog.log', 'a', encoding='utf-8') as file:
            file.write("%(now)s [%(error)s] %(url)s reason: %(reason)s \r\n" %
                       {'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'error': errorType,
                        'url': request.url,
                        'reason': reason})

class IPPOOlS(HttpProxyMiddleware):

    def process_request(self, request, spider):
        args = dict(host='127.0.0.1', port=6379, password='123456', db=0)
        fetcher = ProxyFetcher('zhihu', strategy='greedy', redis_args=args)
        thisip = fetcher.get_proxy()
        print("当前使用proxy是："+ thisip)
        request.meta["proxy"] = fetcher.get_proxy()