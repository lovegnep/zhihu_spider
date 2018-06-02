# -*- coding=utf8 -*-
import os
import re
import json
import time
import random
import datetime
import time
from .province import *
import logging
from scrapy import log
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from zhihu.items import ZhihuPeopleItem, ZhihuRelationItem
from zhihu.constants import Gender, People, HEADER

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

logger=logging.getLogger()

class ZhihuSipder(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["www.96tui.cn"]
    start_urls = [
        "http://weixinqun.96tui.cn/?page=1",
        "http://www.96tui.cn/hufen/?page=1&",
        "http://www.96tui.cn/gongzhonghao/?page=1&",
    ]
    gindex=0
    pindex=0
    oindex=0
    maxgindex=2
    maxpindex=2
    maxoindex=2
    gcount=0
    pcount=0
    ocount=0
    def parse(self, response):
        selector = Selector(response)
        type = 0
        callback=self.parse_group
        nexturls=[]
        groupavatars=[]
        if response.url.rfind('hufen') != -1:
            type = 2
            callback = self.parse_personal
            nexturls=selector.xpath('//ul[@class="qr_code clear"]/li/div/a[@class="thumb_100 relative"]/@href').extract()
            groupavatars = selector.xpath('//ul[@class="qr_code clear"]/li/div/a/img/@src').extract()
        elif response.url.rfind('gongzhonghao') != -1:
            type=3
            callback = self.parse_openid
            nexturls=selector.xpath('//ul[@class="gzh_tuijian clear"]/li/a/@href').extract()
            groupavatars = selector.xpath('//ul[@class="gzh_tuijian clear"]/li/a/img/@src').extract()
        else:
            type=1
            nexturls=selector.xpath('//ul[@class="qr_code clear"]/li/div[@class="thumb"]/a/@href').extract()
            groupavatars = selector.xpath('//ul[@class="qr_code clear"]/li/div/a/img/@src').extract()

        if len(nexturls) != len(groupavatars):
            logger.warn('not enough items. url:%s, urlnum:%d, groupnum:%d', response.url, len(nexturls), len(groupavatars))
            logger.debug('parse:body:'+response.text)
        for index in range(len(nexturls)):
            #time.sleep(random.randint(10, 20))
            #complete_url = 'https://{}{}'.format(self.allowed_domains[0], nexturls[index])
            yield Request(nexturls[index],
                          meta={'type': type,'groupavatar':groupavatars[index]},
                          callback=callback,
                          errback=self.parse_err)
        if self.gindex == 0 and type == 1 and self.maxgindex > 0:
            self.gindex = 1
            for num in range(2, self.maxgindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "http://weixinqun.96tui.cn/?page=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.pindex == 0 and type == 2 and self.maxpindex > 0:
            self.pindex = 1
            for num in range(2, self.maxpindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "http://www.96tui.cn/hufen/?page={}&".format(str(num))
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.oindex == 0 and type == 3 and self.maxoindex > 0:
            self.oindex = 1
            for num in range(2, self.maxoindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "http://www.96tui.cn/gongzhonghao/?page={}&".format(str(num))
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)

    def parse_group(self, response):
        self.gcount = self.gcount+1
        logger.debug('parse_group count:%d',self.gcount)
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']
        logger.info('parse_group:groupavatar:'+groupavatar)
        selector = Selector(response)
        groupQR = selector.xpath('//div[@id="qr_info"]/div[@class="qr"]/div/img/@src').extract()[0].strip()
        groupname=selector.xpath('//div[@class="v_title3 clear"]/h1/text()').extract()[0].strip()
        abstract = selector.xpath('//div[@class="v_notify"]/text()').extract()[0].strip()
        #otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        #industry = otherinfos[0].strip()
        #location = getLocationByName(otherinfos[1].strip())
        grouptag = selector.xpath('//a[@class="keywords"]/text()').extract()
        tags = jiebaStr(groupname,abstract,','.join(grouptag))
        createTime = datetime.datetime.now()
        updateTime = createTime
        masterwx = response.xpath('//div[@class="main clear"]/div[@class="l"]/div/text()').extract()[2].strip()
        masterwx=masterwx[masterwx.find(':')+1:len(masterwx)]
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1:
            logger.warn('invalid gorm: url:%s, groupQR:%s', response.url, groupQR)

        item = ZhihuPeopleItem(
            type=1,
            source=2,
            groupname=groupname,
            abstract=abstract,
            grouptag=grouptag,
            masterwx=masterwx,
            groupavatar=groupavatar,
            groupQR=groupQR,
            masterQR='',
            createTime=createTime,
            updateTime=updateTime,
            tags=tags,
            delete=False,
            secret=False
        )
        yield item
    def parse_personal(self, response):
        self.pcount = self.pcount+1
        logger.debug('parse_personal count:%d',self.pcount)
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']
        logger.info('parse_personal:groupavatar:'+groupavatar)
        selector = Selector(response)
        groupQR = selector.xpath('//div[@id="qr_info"]/div[@class="qr"]/div/img/@src').extract()[0].strip()
        groupname=selector.xpath('//div[@class="v_title3 clear"]/h1/text()').extract()[0].strip()
        abstract = selector.xpath('//div[@class="v_notify"]/text()').extract()[0].strip()
        grouptag = selector.xpath('//a[@class="keywords"]/text()').extract()

        tags=jiebaStr(groupname,abstract,','.join(grouptag))
        createTime = datetime.datetime.now()
        updateTime = createTime
        masterwx = selector.xpath('//div[@class="main clear"]/div[@class="l"]/div/text()').extract()[2].strip()
        masterwx=masterwx[masterwx.find(':')+1:len(masterwx)]
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1:
            logger.warn('invalid groupQR: url:%s, groupQR:%s', response.url, groupQR)
        item = ZhihuPeopleItem(
            type=2,
            source=2,
            groupname=groupname,
            abstract=abstract,
            grouptag=grouptag,
            masterwx=masterwx,
            groupavatar=groupavatar,
            groupQR=groupQR,
            createTime=createTime,
            updateTime=updateTime,
            tags=tags,
            delete=False,
            secret=False
        )
        yield item
    def parse_openid(self, response):
        self.ocount = self.ocount+1
        logger.debug('parse_openid count:%d',self.ocount)
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']
        logger.info('parse_openid:groupavatar:'+groupavatar)
        selector = Selector(response)
        groupQR = selector.xpath('//div[@id="qr_info"]/div[@class="qr"]/div/img/@src').extract()[0].strip()
        groupname=selector.xpath('//div[@class="v_title3 clear"]/h1/text()').extract()[0].strip()
        abstract = selector.xpath('//div[@class="clear main"]/div[@class="l"]/div/text()').extract()[3].strip()
        grouptag = selector.xpath('//a[@class="keywords"]/text()').extract()

        tags=jiebaStr(groupname,abstract,','.join(grouptag))
        createTime = datetime.datetime.now()
        updateTime = createTime
        masterwx = selector.xpath('//div[@class="clear main"]/div[@class="l"]/div/text()').extract()[2].strip()
        masterwx=masterwx[masterwx.find(':')+1:len(masterwx)]
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1:
            logger.warn('invalid groupQR: url:%s, groupQR:%s', response.url, groupQR)
        item = ZhihuPeopleItem(
            type=3,
            source=2,
            groupname=groupname,
            abstract=abstract,
            grouptag=grouptag,
            masterwx=masterwx,
            groupavatar=groupavatar,
            groupQR=groupQR,
            createTime=createTime,
            updateTime=updateTime,
            tags=tags,
            delete=False,
            secret=False
        )
        yield item

    def parse_err(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        logger.warn('request error happen:{}'.format(failure))
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
