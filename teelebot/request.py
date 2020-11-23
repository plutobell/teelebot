# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modify: 2020-11-23
'''
import os

import requests
import inspect
from .logger import _logger
from traceback import extract_stack
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class _Request(object):
    """
    接口请求类
    """
    def __init__(self, thread_pool_size, url, debug=False):
        self.__url = url
        self.__debug = debug
        self.__session = self.__connection_session(
            pool_connections=thread_pool_size,
            pool_maxsize=thread_pool_size * 2
        )

    def __del__(self):
        self.__session.close()

    def __connection_session(self, pool_connections=10, pool_maxsize=10, max_retries=5):
        """
        连接池
        """
        session = requests.Session()
        session.verify = False

        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections,
                                                pool_maxsize=pool_maxsize, max_retries=max_retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def __debug_info(self, result):
        """
        debug模式
        """
        if self.__debug and not result.get("ok"):
            os.system("")  # "玄学"解决Windows下颜色显示失效的问题...
            stack_info = extract_stack()
            if len(stack_info) > 8:  # 插件内
                _logger.debug("\033[1;31m" + \
                            "Request failed" + " - " + \
                            "From:" + stack_info[-3][2] + " - " + \
                            "Path:" + stack_info[5][0] + " - " + \
                            "Line:" + str(stack_info[5][1]) + " - " + \
                            "Method:" + stack_info[6][2] + " - " + \
                            "Result:" + str(result) + \
                            "\033[0m")
            elif len(stack_info) > 3:  # 外部调用
                _logger.debug("\033[1;31m" + \
                            "Request failed" + " - " + \
                            "From:" + stack_info[0][0] + " - " + \
                            "Path:" + stack_info[1][0] + " - " + \
                            "Line:" + str(stack_info[0][1]) + " - " + \
                            "Method:" + stack_info[1][2] + " - " + \
                            "Result:" + str(result) + \
                            "\033[0m")

    def post(self, addr):
        try:
            with self.__session.post(self.__url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok"):
                    return req.json().get("result")
                elif not req.json().get("ok"):
                    return req.json().get("ok")
        except:
            return False

    def postFile(self, addr, file_data):
        try:
            with self.__session.post(self.__url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok"):
                    return req.json().get("result")
                elif not req.json().get("ok"):
                    return req.json().get("ok")
        except:
            return False

    def postJson(self, addr, json):
        try:
            with self.__session.get(self.__url + addr, json=json) as req:
                self.__debug_info(req.json())
                if req.json().get("ok"):
                    return req.json().get("result")
                elif not req.json().get("ok"):
                    return req.json().get("ok")
        except:
            return False

    def get(self, addr):
        try:
            with self.__session.get(self.__url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok"):
                    return req.json().get("result")
                elif not req.json().get("ok"):
                    return req.json().get("ok")
        except:
            return False


