# -*- coding=utf8 -*-
import os
import re
import json
import time
import random
import datetime
import time
import province
from urllib import urlencode
from scrapy import log
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from zhihu.items import ZhihuPeopleItem, ZhihuRelationItem
from zhihu.constants import Gender, People, HEADER

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class ZhihuSipder(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["www.weixinqun.com"]
    start_urls = [
        "https://www.weixinqun.com/group?p=0",
        "https://www.weixinqun.com/personal?p=0",
        "https://www.weixinqun.com/openid?p=0"
    ]
    gindex=0
    pindex=0
    oindex=0
    maxindex=10
    def parse(self, response):
        end=len(response.url)
        if response.url.rfind('?') != -1:
            end = response.url.rfind('?')
        name=response.url[(response.url.rfind('/')+1):end]
        type=0
        if name=="group":
            type=1
        elif name=="personal":
            type=2
        elif name=="openid":
            type=3

        selector = Selector(response)
        xparse='//div[@class="border5"]/a[contains(@href, "/'+name+'?id=")]/@href'
        nexturls = selector.xpath(xparse).extract()

        for index in range(len(nexturls)):
            print index
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], nexturls[index])
            yield Request(complete_url,
                          meta={'type': type},
                          callback=self.parse_follow,
                          errback=self.parse_err)
        if self.gindex == 0 and type==1:
            self.gindex = 1
            for num in range(1,self.maxindex):
                print 'num:',num
                time.sleep(random.randint(1,5) )
                nexturl = "https://www.weixinqun.com/"+name+"?p="+str(num)
                yield Request(nexturl,callback=self.parse,errback=self.parse_err)
        if self.pindex == 0 and type==2:
            self.pindex = 1
            for num in range(1,self.maxindex):
                print 'num:',num
                time.sleep(random.randint(1,5) )
                nexturl = "https://www.weixinqun.com/"+name+"?p="+str(num)
                yield Request(nexturl,callback=self.parse,errback=self.parse_err)
        if self.oindex == 0 and type==3:
            self.oindex = 1
            for num in range(1,self.maxindex):
                print 'num:',num
                time.sleep(random.randint(1,5) )
                nexturl = "https://www.weixinqun.com/"+name+"?p="+str(num)
                yield Request(nexturl,callback=self.parse,errback=self.parse_err)

    def parse_follow(self, response):

        type = response.meta['type']
        selector = Selector(response)
        qrsrc=''
        if type==3:
            qrsrc = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]
        elif type==1:
            qrsrc=selector.xpath('//div[@class="iframe"]/span[@class="shiftcode"]/img/@src').extract()[1]
        elif type==2:
            qrsrc = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]

        if qrsrc=='':
            self.logger.error('none src: url:%s, type:%d',response.url, type)
            return
        item = ZhihuPeopleItem(
            type=type,
            qrsrc=qrsrc,
        )
        yield item

    def parse_err(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s, statuscode:%d', response.url, response.status)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
