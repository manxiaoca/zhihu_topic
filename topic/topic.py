#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import time

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath('..'))

from util._log import log
from util._mysql import MysqlHandler

from util import common
from util import crawler
from util import headers
from util import cookie

from config import conf


""" 本程序用以获取指定话题下所有问题链接
"""

## 获取配置参数
SETTINGS = conf.SETTINGS

## 数据库连接
MYSQLHANDLER = MysqlHandler(SETTINGS)

## topic入口链接
crawl_topic_url = conf.crawl_topic_url
## topic分页链接
page_topic_url = conf.page_topic_url

## question id
QUESTION_ID = list()


class Topic:
    def __init__(self, topic_id):
        """ 初始化topic_id, topic_url
        """
        self.topic_id = topic_id
    
    @classmethod
    def from_topic(cls, topic_id):
        return cls(topic_id)
    
    def crawl_topic(self):
        """ 根据topic_url抓取topic页面
        """
        '''
        for _file in os.listdir('./data/topics/19610713'):
            with open('./data/topics/19610713/{}'.format(_file), 'rb') as _r:
                content = _r.read()
            self.extract_question_id(content)
        return QUESTION_ID
        '''
        max_page = self.get_topic_max_page()
        self.crawl_topic_page(max_page)
        return QUESTION_ID
    
    def crawl_topic_page(self, max_page):
        """ 分页面下载
        """
        if not max_page or max_page == 0:
            url = crawl_topic_url.format(self.topic_id)
            content = crawler.crawl(url)
            if not content:
                return
            self.webpage_save(1, content)
            self.extract_question_id(content)
        else:
            for i in range(1, max_page+1):
                url = page_topic_url.format(self.topic_id, i)
                content = crawler.crawl(url)
                if not content:
                    continue
                self.webpage_save(i, content)
                self.extract_question_id(content)
                time.sleep(0.5)
    
    def extract_question_id(self, content):
        """ 从topic页面中提取question链接
        """
        if not content:
            return
        global QUESTION_ID
        questions = re.findall('link itemprop="url" href="/question/(\d+)', content)
        for q in questions:
            QUESTION_ID.append(q)
        
    def get_topic_max_page(self):
        """ 根据入口链接找出此topic下页面总数
        """
        url = crawl_topic_url.format(self.topic_id)
        content = crawler.crawl(url)
        max_page = 0
        try:
            page_num = re.findall('\?page=(\d+)', content)
            if page_num:
                max_page = max(int(i) for i in page_num)
        except Exception, e:
            log.error('topic_topic: get_topic_max_page except={}'.format(e))
        return max_page
    
    def webpage_save(self, i, content):
        """ 网页文件存储
        """
        file_name = '{}/data/topics/{}/page_{}.html'.format(os.path.abspath('.'), self.topic_id, i)
        with open(file_name, 'wb') as _w:
            _w.write(content)

        
def test():
    """ 测试
    """
    Topic.from_topic('19610713').crawl_topic()
    print QUESTION_ID

if __name__ == '__main__':
    test()
