# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ZhihuPeopleItem(Item):
    type = Field()
    qrsrc = Field()

class ZhihuRelationItem(Item):
    """知乎用户关系

    Attributes:
        zhihu_id 知乎id
        user_list 用户列表
        user_type 用户类型（1关注的人 2粉丝）
    """
    zhihu_id = Field()
    user_list = Field()
    user_type = Field()