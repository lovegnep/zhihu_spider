# -*- coding=utf8 -*-
import os
import re
import json
import time
import datetime
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
        "https://www.weixinqun.com/group?p=1",
        "https://www.weixinqun.com/group?p=2",
        "https://www.weixinqun.com/group?p=3",
        "https://www.weixinqun.com/group?p=4",
        "https://www.weixinqun.com/group?p=5"
    ]
    index=0
    maxindex=10
    def parse(self, response):
        """
        解析用户主页
        """
        selector = Selector(response)
        timeago = selector.xpath('//div[@class="border5"]/p[@class="wxNum ellips"]/span[@class="caaa"]/text()').extract()
        groupavatars = selector.xpath('//a[contains(@href, "/group?id=")]/img/@src').extract()
        groupnames = selector.xpath('//a[contains(@href, "/group?id=")]/@title').extract()
        locations = selector.xpath('//a[@class="btnCity"]/text()').extract()
        nexturls = selector.xpath('//div[@class="border5"]/a[contains(@href, "/group?id=")]/@href').extract()
        print nexturls, len(nexturls)
        for index in range(len(nexturls)):
            print index
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], nexturls[index])
            tmpitem = {
                'groupname':groupnames[index],
                'groupavatar':groupavatars[index],
                'locations':locations[index]
            }
            yield Request(complete_url,
                          meta={'tmpitem': tmpitem},
                          callback=self.parse_follow,
                          errback=self.parse_err)
        '''
        for num in range(1,self.maxindex):
            print 'num:',num
            nexturl = "https://www.weixinqun.com/group?p="+str(num)
            yield Request(nexturl,callback=self.parse,errback=self.parse_err)
       '''
    def parse_follow(self, response):
        """
        解析follow数据
        """
        tmpitem = response.meta['tmpitem']
        selector = Selector(response)
        qrs = selector.xpath('//span[@class="shiftcode"]/img/@src').extract()
        groupQR = qrs[1]
        masterQR = qrs[0]
        abstract = selector.xpath('//span[@class="des_info_text2"]/text()').extract()[0]
        otherinfos = selector.xpath('//ul[@class="other-info"]/li/a/text()').extract()
        industry = otherinfos[0]
        location = province.getLocationByName(otherinfos[1].strip())
        grouptag = province.rmspace(re.split('[ |/,]',otherinfos[2].strip()))
        tags = province.jiebaStr(tmpitem['groupname'],abstract,otherinfos[2])
        createTime = selector.xpath('//li/text()').re(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')[0]
        createTime = datetime.datetime.strptime(createTime, "%Y-%m-%d %H:%M:%S")
        updateTime = createTime
        masterwx = response.xpath('//div[@class="clearfix"]/ul/li/span[@class="des_info_text2"]/text()').extract()[1]
        item = ZhihuPeopleItem(
            type=1,
            source=2,
            industry=industry,
            location=location,
            groupname=tmpitem['groupname'],
            abstract=abstract,
            grouptag=grouptag,
            masterwx=masterwx,
            groupavatar=tmpitem['groupavatar'],
            groupQR=groupQR,
            masterQR=masterQR,
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
