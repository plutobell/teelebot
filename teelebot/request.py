# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modification: 2023-05-14
'''
import json
import requests

from .logger import _logger
from traceback import extract_stack


class _Request(object):
    """
    Request Class
    """
    def __init__(self, thread_pool_size, url, debug=False, proxies={"all": None}):
        self.__url = url
        self.__debug = debug
        self.__proxies = proxies
        self.__session = self.__connection_session(
            pool_connections=thread_pool_size,
            pool_maxsize=thread_pool_size * 2
        )

    def __del__(self):
        self.__session.close()

    def __connection_session(self, pool_connections=10, pool_maxsize=10, max_retries=5):
        """
        Connection Pool
        """
        session = requests.Session()
        session.verify = False
        # session.trust_env = False
        session.proxies.update(self.__proxies)
        

        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections,
                                                pool_maxsize=pool_maxsize, max_retries=max_retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def __debug_info(self, method_name, result):
        """
        Debug mode
        """
        if self.__debug and not result.get("ok"):
            stack_info = extract_stack()
            if len(stack_info) > 8:  # Plugin internal call
                _logger.error(
                    "Request failed" + " - " + \
                    "From:" + stack_info[-3][2] + " - " + \
                    "Path:" + stack_info[5][0] + " - " + \
                    "Line:" + str(stack_info[5][1]) + " - " + \
                    "Method:" + method_name + " - " + \
                    "Result:" + str(result)) # function name: stack_info[6][2]
            elif len(stack_info) > 3:  # External call
                _logger.error(
                    "Request failed" + " - " + \
                    "From:" + stack_info[0][0] + " - " + \
                    "Path:" + stack_info[1][0] + " - " + \
                    "Line:" + str(stack_info[0][1]) + " - " + \
                    "Method:" + method_name + " - " + \
                    "Result:" + str(result)) # function name: stack_info[6][2]

    def postEverything(self, method_name, **kwargs):

        inputmedia_methods = ["sendMediaGroup", "editMessageMedia"]
        is_inputmedia = False
        inputmedia_param_name = "files"
        if method_name in inputmedia_methods:
            is_inputmedia = True

        data, files = {}, {}
        for key, value in kwargs.items():
            if not is_inputmedia and key == inputmedia_param_name:
                pass
            elif is_inputmedia and key == inputmedia_param_name:
                files = value
            elif isinstance(value, bytes):
                files[key] = value
            elif isinstance(value, dict):
                data[key] = json.dumps(value)
            elif isinstance(value, list):
                data[key] = json.dumps(value)
            else:
                data[key] = value

        # print(data, "\n", files)
        try:
            with self.__session.post(url=f'{self.__url}{method_name}', data=data, files=files) as req:
                self.__debug_info(method_name, req.json())
                if req.json().get("ok", False):
                    return req.json().get("result")
                else:
                    return req.json().get("ok")
        except Exception as e:
            print("Error:", str(e))
            return False


