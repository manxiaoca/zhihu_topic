#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import re
import time

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath('..'))

from lxml import etree

from util._log import log
from util._mysql import MysqlHandler

from util import common
from util import crawler
from util import headers
from util import cookie

from config import conf


""" 本程序用以下载question页面并解析
"""

## 获取配置参数
SETTINGS = conf.SETTINGS

## 数据库连接
MYSQLHANDLER = MysqlHandler(SETTINGS)

## topic入口链接
crawl_question_url = conf.crawl_question_url
## topic分页链接
page_topic_url = conf.page_topic_url

## question id
QUESTION_ID = list()


class Question:
    def __init__(self, question_id, topic_id):
        self.question_id = question_id
        self.topic_id = topic_id
        self.question_url = ''
        self.question_title = ''
        self.question_text = ''
        self.follower_count = ''
        self.scan_count = ''
        self.answer_count = ''
        self.question_tag = ''
        
    @classmethod
    def from_question(cls, question_id, topic_id):
        return cls(question_id, topic_id)
    
    def crawl_question(self):
        """ 根据question_url抓取question页面
        """
        self.question_url = self.get_question_url()
        content = crawler.crawl(self.question_url)
        #with open('./data/questions/38589246.html', 'rb') as _r:
        #    content = _r.read()
        if not content:
            return
        self.webpage_save(content)
        return self.parse_question(content)
        
    def get_question_url(self):
        """ 生成question链接
        """
        return crawl_question_url.format(self.question_id)

    def parse_question(self, content):
        """ 解析question页面
        """
        html = etree.HTML(content)
        question_header = html.xpath('//div[@class="QuestionHeader"]/div[@class="QuestionHeader-content"]')
        if not question_header:
            return
        question_tag = question_header[0].xpath(
            './div[@class="QuestionHeader-main"]/div[@class="QuestionHeader-topics"]/div/span/a/div/div/text()')
        _title = question_header[0].xpath('./div[@class="QuestionHeader-main"]/h1/text()')
        question_title = _title[0] if _title else ''
        _text = question_header[0].xpath(
            './div[@class="QuestionHeader-main"]/div[@class="QuestionHeader-detail"]/div/span/text()')
        question_text = _text[0] if _text else ''
        '''
        _follower = question_header[0].xpath(
            './div[@class="QuestionHeader-side"]/div[@class="QuestionFollowStatus"]/div/button/div[@class="NumberBoard-value"]/text()')
        follower_count = _follower[0] if _follower else ''
        _scan = question_header[0].xpath(
            './div[@class="QuestionHeader-side"]/div[@class="QuestionFollowStatus"]/div/div[@class="NumberBoard-item"]/div[@class="NumberBoard-value"]/text()')
        scan_count = _scan[0] if _scan else ''
        '''
        follower_count = scan_count = ''
        follow_scan = re.findall('NumberBoard-value">(\d+)', content)
        if len(follow_scan) == 2:
            follower_count, scan_count = follow_scan
        else:
            log.info('question_parse_question: len(follow_scan) != 2')
        _answer = html.xpath('//div[@class="List-header"]/h4/span/text()')
        _answer_count = _answer[0] if _answer else ''
        if _answer_count:
            answer_count = re.search('(\d+)', _answer_count).group(1) if re.search('(\d+)', _answer_count) else '0'
        else:
            answer_count = '0'
        '''
        print question_tag
        print question_title
        print question_text
        print follower_count
        print scan_count
        print answer_count
        '''
        return {
            'question_url': self.question_url,
            'question_tag': question_tag,
            'question_title': question_title,
            'question_text': question_text,
            'follower_count': follower_count,
            'scan_count': scan_count,
            'answer_count': answer_count
        }
    
    def webpage_save(self, content):
        """ 网页文件存储
        """
        file_name = '{}/data/questions/{}.html'.format(os.path.abspath('.'), self.question_id)
        with open(file_name, 'wb') as _w:
            _w.write(content)


def main():
    """ 主函数
    """


if __name__ == '__main__':
    main()