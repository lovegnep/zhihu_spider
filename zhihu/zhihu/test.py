# coding=UTF-8
import jieba
import re
print re.split(',',','.join(jieba.cut_for_search(u'我是中国人')))