# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ZhihuPeopleItem(Item):
    """知乎用户属性

    Attributes:
        nickname 用户名
        zhihu_id 用户id
        location 位置
        business 行业
        gender 性别
        employment 公司
        position 职位
        education 教育情况
        image_url 头像图片url
    """

    uploader = Field()
    type = Field()
    source = Field()
    industry = Field()
    location = Field()
    groupname = Field()
    abstract = Field()
    grouptag = Field()
    tags = Field()
    masterwx = Field()
    groupavatar = Field()
    groupQR = Field()
    masterQR = Field()
    createTime = Field()
    updateTime = Field()
    viewCount = Field()
    likeCount = Field()
    commentCount = Field()
    gender = Field()
    birthday = Field()
    delete = Field()
    secret = Field()
    f5Time = Field()



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