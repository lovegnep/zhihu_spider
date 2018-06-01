
import logging
import codecs
import datetime
import random
import time
# 导入官方文档对应的HttpProxyMiddleware
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
from zhihu.client.py_cli import ProxyFetcher
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
logger=logging.getLogger()


class JobboleProxyMiddleware(object):

    def __init__(self):
        args = dict(host='127.0.0.1', port=6379, password='123456', db=0)
        self.scheme = 'wcgroup'
        self.fetcher = ProxyFetcher(self.scheme, strategy='greedy', redis_args=args)
        self.proxy = self.get_next_proxy()
        self.start = time.time() * 1000

    def process_request(self, request, spider):
        self.start = time.time() * 1000
        logger.info("this is request ip:" + self.proxy)
        request.meta['proxy'] = self.proxy
        request.meta['start'] = self.start

        return None

    def process_response(self, request, response, spider):
        end = time.time() * 1000
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            self.fetcher.proxy_feedback('failure', self.proxy)
            logger.info('Current ip is blocked! The proxy is {}'.format(self.proxy))
            # 对当前request换下一个代理
            self.proxy = self.get_next_proxy()
            request.meta['proxy'] = self.proxy
            return request
        else:
            spider.logger.info('Request succeeded! The proxy is {}'.format(self.proxy))
            # if you use greedy strategy, you must feedback
            duration=int(end - request.meta['start'])
            self.fetcher.proxy_feedback('success', self.proxy, duration)
            return response

    def process_exception(self, request, exception, spider):
        logger.error('Request failed!The proxy is {}, {}. Exception:{}'.format(request.meta['proxy'], self.proxy, exception))
        # it's important to feedback, otherwise you may use the bad proxy next time
        self.fetcher.proxy_feedback('failure', self.proxy)
        # 对当前request换下一个代理
        self.proxy = self.get_next_proxy()
        request.meta['proxy'] = self.proxy
        return request

    def get_next_proxy(self):
        # 获取一个可用代理
        return self.fetcher.get_proxy()

    def spider_opened(self, spider):
        logger.info('Spider opened: %s' % spider.name)

class monitor(object):
    def process_request(self, request, spider):
        logger.info('monitor process_request:%s', request.url)

    def process_response(self, request, response, spider):
        logger.info('monitor process_response:%d',response.status)
        if response.status != 200:
            return request
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
        return None


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            logger.info('RotateUserAgentMiddleware: new ua:'+ua)
            request.headers.setdefault('User-Agent', ua)

            # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape

    # for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1", \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
