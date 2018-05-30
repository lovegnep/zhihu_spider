# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from zhihu.spiders.province import *

from pymongo import MongoClient
from zhihu.settings import MONGO_URI, PROJECT_DIR
from zhihu.items import ZhihuPeopleItem, ZhihuRelationItem
from zhihu.tools.async import download_pic


class ZhihuPipeline(object):
    """
    存储数据
    """
    def __init__(self, mongo_uri, mongo_db, image_dir):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.image_dir = '/home/gnep/work/zhihu_spider/images'
        self.client = None
        self.db= None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=MONGO_URI,
            mongo_db='wcgroup',
            image_dir=os.path.join(PROJECT_DIR, 'images')
        )

    def open_spider(self, spider):
        #self.client = MongoClient(self.mongo_uri)
        self.client = MongoClient('47.98.136.138:20005',username='lovegnep_wcgroup',password='liuyang15',authSource='wcgroup',authMechanism='SCRAM-SHA-1')
        self.db = self.client[self.mongo_db]
        if not os.path.exists(self.image_dir):
            os.mkdir(self.image_dir)

    def close_spider(self, spider):
        self.client.close()

    def downimg(self, src, type1,type2):
        pid = os.getpid()
        dbsrc = calcDbSrc(src,pid,type1, type2)
        savename = str(pid)+'_'+str(type1)+'_'+str(type2)+'_'+getImgName(src)
        savename = os.path.join(self.image_dir, savename)
        download_pic.delay(src, savename)

    def _process_people(self, item):
        """
        存储用户信息
        """
        type=item['type']
        if type==1:
            self._process_group(item)
        elif type==2:
            self._process_personal(item)
        elif type==3:
            self._process_openid(item)

    def _process_group(self, item):
        """
        存储用户信息
        """
        pid = os.getpid()
        gavaarc=item['groupavatar']
        gqrsrc=item['groupQR']
        mqrsrc=item['masterQR']
        item['groupavatar'] = calcDbSrc(item['groupavatar'], pid,1,1)
        item['groupQR'] = calcDbSrc(item['groupQR'], pid,1,2)
        item['masterQR'] = calcDbSrc(item['masterQR'], pid,1,3)
        collection = self.db['qrmodels']
        groupQR = item['groupQR']
        collection.update({'groupQR': groupQR},
                          dict(item), upsert=True)
        self.downimg(gavaarc, 1,1)
        self.downimg(gqrsrc, 1,2)
        self.downimg(mqrsrc, 1,3)
    def _process_personal(self, item):
        """
        存储用户信息
        """
        pid = os.getpid()
        gavaarc=item['groupavatar']
        gqrsrc=item['groupQR']

        item['groupavatar'] = calcDbSrc(item['groupavatar'], pid,2,1)
        item['groupQR'] = calcDbSrc(item['groupQR'], pid,2,2)

        collection = self.db['qrmodels']

        collection.update({'masterwx': item['masterwx'], 'source':2},
                          dict(item), upsert=True)
        self.downimg(gavaarc, 2,1)
        self.downimg(gqrsrc, 2,2)
    def _process_openid(self, item):
        """
        存储用户信息
        """
        pid = os.getpid()
        gavaarc=item['groupavatar']
        gqrsrc=item['groupQR']
        item['groupavatar'] = calcDbSrc(item['groupavatar'], pid,3,1)
        item['groupQR'] = calcDbSrc(item['groupQR'], pid,3,2)

        collection = self.db['qrmodels']

        collection.update({'masterwx': item['masterwx'], 'source':2},
                          dict(item), upsert=True)
        self.downimg(gavaarc, 3,1)
        self.downimg(gqrsrc, 3,2)

    def _process_relation(self, item):
        """
        存储人际拓扑关系
        """
        collection = self.db['relation']

        data = collection.find_one({
            'zhihu_id': item['zhihu_id'],
            'user_type': item['user_type']})
        if not data:
            self.db['relation'].insert(dict(item))
        else:
            origin_list = data['user_list']
            new_list = item['user_list']
            data['user_list'] = list(set(origin_list) | set(new_list))
            collection.update({'zhihu_id': item['zhihu_id'],
                               'user_type': item['user_type']}, data)

    def process_item(self, item, spider):
        """
        处理item
        """
        if isinstance(item, ZhihuPeopleItem):
            self._process_people(item)
        elif isinstance(item, ZhihuRelationItem):
            self._process_relation(item)
        return item
