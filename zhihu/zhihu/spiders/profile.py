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
    allowed_domains = ["www.weixinqun.com"]
    start_urls = [
        "https://www.weixinqun.com/group?p=0",
        "https://www.weixinqun.com/personal?p=0",
        "https://www.weixinqun.com/openid?p=0"
    ]
    gindex=0
    pindex=0
    oindex=0
    maxgindex=22
    maxpindex=2329
    maxoindex=185
    gcount=0
    pcount=0
    ocount=0
    def parse(self, response):
        end = len(response.url)
        if response.url.rfind('?') != -1:
            end = response.url.rfind('?')
        name = response.url[(response.url.rfind('/') + 1):end]
        type = 0
        callback=self.parse_group
        if name == "group":
            type = 1
        elif name == "personal":
            type = 2
            callback = self.parse_personal
        elif name == "openid":
            type = 3
            callback = self.parse_openid

        selector = Selector(response)
        xparse = '//div[@class="border5"]/a[contains(@href, "/' + name + '?id=")]/@href'
        nexturls = selector.xpath(xparse).extract()
        groupavatars = selector.xpath('//a[contains(@href, "/'+name+'?id=")]/img/@src').extract()
        if len(nexturls) != 42 or len(groupavatars) != 42:
            logger.warn('not enough items. url:%s, urlnum:%d, groupnum:%d', response.url, len(nexturls), len(groupavatars))
        for index in range(len(nexturls)):
            #time.sleep(random.randint(10, 20))
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], nexturls[index])
            yield Request(complete_url,
                          meta={'type': type,'groupavatar':groupavatars[index]},
                          callback=callback,
                          errback=self.parse_err)
        if self.gindex == 0 and type == 1:
            self.gindex = 1
            for num in range(1, self.maxgindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.pindex == 0 and type == 2:
            self.pindex = 1
            for num in range(1, self.maxpindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.oindex == 0 and type == 3:
            self.oindex = 1
            for num in range(1, self.maxoindex):
                #time.sleep(random.randint(10, 20))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)

    def parse_group(self, response):
        self.gcount = self.gcount+1
        logger.debug('parse_group count:%d',self.gcount)
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']

        selector = Selector(response)
        qrs = selector.xpath('//span[@class="shiftcode"]/img/@src').extract()
        groupQR = qrs[1]
        masterQR = qrs[0]
        groupname=selector.xpath('//span[@class="des_info_text"]/b/text()').extract()[0].strip()
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0].strip()
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0].strip()
        location = getLocationByName(otherinfos[1].strip())
        grouptag = rmspace(re.split('[ |/,.，。]',otherinfos[2].strip()))
        tags = jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1 or masterQR.find('http') == -1:
            logger.warn('invalid gorm: url:%s, groupQR:%s, masterQR:%s', response.url, groupQR, masterQR)

        item = ZhihuPeopleItem(
            type=1,
            source=2,
            industry=industry,
            location=location,
            groupname=groupname,
            abstract=abstract,
            grouptag=grouptag,
            masterwx=masterwx,
            groupavatar=groupavatar,
            groupQR=groupQR,
            masterQR=masterQR,
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

        selector = Selector(response)

        groupQR = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]
        groupname=selector.xpath('//span[@class="des_info_text"]/b/text()').extract()[0].strip()
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0].strip()
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0].strip()
        location = getLocationByName(otherinfos[1].strip())
        grouptag = rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1:
            logger.warn('invalid groupQR: url:%s, groupQR:%s', response.url, groupQR)
        item = ZhihuPeopleItem(
            type=2,
            source=2,
            industry=industry,
            location=location,
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

        selector = Selector(response)
        groupQR = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]
        groupname=selector.xpath('//span[@class="des_info_text"]/b/text()').extract()[0].strip()
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0].strip()
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0].strip()
        location = getLocationByName(otherinfos[1].strip())
        grouptag = rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
        if groupavatar.find('http') == -1:
            logger.warn('invalid groupavatar: url:%s, gavatarurl:%s', response.url, groupavatar)
        if groupQR.find('http') == -1:
            logger.warn('invalid groupQR: url:%s, groupQR:%s', response.url, groupQR)
        item = ZhihuPeopleItem(
            type=3,
            source=2,
            industry=industry,
            location=location,
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
        logger.warn('request error happen:',failure)
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
