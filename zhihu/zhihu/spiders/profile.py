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
    maxgindex=10
    maxpindex=10
    maxoindex=10
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

        for index in range(len(nexturls)):
            print index
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], nexturls[index])
            yield Request(complete_url,
                          meta={'type': type,'groupavatar':groupavatars[index]},
                          callback=callback,
                          errback=self.parse_err)
        if self.gindex == 0 and type == 1:
            self.gindex = 1
            for num in range(1, self.maxgindex):
                print 'num:', num
                time.sleep(random.randint(1, 5))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.pindex == 0 and type == 2:
            self.pindex = 1
            for num in range(1, self.maxpindex):
                print 'num:', num
                time.sleep(random.randint(1, 5))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)
        if self.oindex == 0 and type == 3:
            self.oindex = 1
            for num in range(1, self.maxoindex):
                print 'num:', num
                time.sleep(random.randint(1, 5))
                nexturl = "https://www.weixinqun.com/" + name + "?p=" + str(num)
                yield Request(nexturl, callback=self.parse, errback=self.parse_err)

    def parse_group(self, response):
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
        location = province.getLocationByName(otherinfos[1].strip())
        grouptag = province.rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = province.jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
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
            tags=tags
        )
        yield item
    def parse_personal(self, response):
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']

        selector = Selector(response)

        groupQR = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]
        groupname=selector.xpath('//span[@class="des_info_text"]/b/text()').extract()[0].strip()
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0].strip()
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0].strip()
        location = province.getLocationByName(otherinfos[1].strip())
        grouptag = province.rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = province.jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
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
            tags=tags
        )
        yield item
    def parse_openid(self, response):
        type=response.meta['type']
        groupavatar=response.meta['groupavatar']

        selector = Selector(response)
        groupQR = selector.xpath('//div[@class="iframe"]/img/@src').extract()[0]
        groupname=selector.xpath('//span[@class="des_info_text"]/b/text()').extract()[0].strip()
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0].strip()
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0].strip()
        location = province.getLocationByName(otherinfos[1].strip())
        grouptag = province.rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = province.jiebaStr(groupname,abstract,otherinfos[2].strip())
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1].strip()
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
            tags=tags
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
