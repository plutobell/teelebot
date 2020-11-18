# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modify: 2020-11-18
'''
import logging as __logging

__logging.basicConfig(level=__logging.DEBUG,
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(levelname)s - %(message)s')
__logging.getLogger("urllib3").setLevel(__logging.WARNING)

_logger = __logging.getLogger(__name__)