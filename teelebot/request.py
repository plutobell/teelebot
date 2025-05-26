# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modification: 2025-05-26
'''
import io
import json
import traceback
import requests

from .logger import get_logger
from traceback import extract_stack
from concurrent.futures import ThreadPoolExecutor
_logger = get_logger()


class _Request(object):
    """
    Request Class
    """
    def __init__(self, thread_pool_size, url, message_deletor, hide_info, debug=False, proxies={"all": None}):
        self.__url = url
        self.__message_deletor = message_deletor
        self.__hide_info = hide_info
        self.__debug = debug
        self.__proxies = proxies

        self.__session = self.__connection_session(
            pool_connections=thread_pool_size,
            pool_maxsize=thread_pool_size * 2
        )
        self.__thread_pool = ThreadPoolExecutor(
            max_workers=thread_pool_size * 2)

    def __del__(self):
        self.__session.close()
        self.__thread_pool.shutdown(wait=True)

    def __connection_session(self, pool_connections=10, pool_maxsize=10, max_retries=5):
        """
        Connection Pool
        """
        session = requests.Session()
        session.verify = False

        if isinstance(self.__proxies, dict):
            if self.__proxies and self.__proxies != {"all": None}:
                session.trust_env = False
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

        run_in_thread = False
        run_in_thread_param_name = "run_in_thread"
        if run_in_thread_param_name in list(kwargs.keys()):
            value = kwargs.get(run_in_thread_param_name, False)
            if isinstance(value, bool):
                run_in_thread = value

        del_msg_after = -1
        del_msg_after_param_name = "del_msg_after"
        if del_msg_after_param_name in list(kwargs.keys()):
            value = kwargs.get(del_msg_after_param_name, False)
            if isinstance(value, int):
                del_msg_after = value

        data, files = {}, {}
        for key, value in kwargs.items():
            if isinstance(value, io.BufferedReader):
                value = value.read()

            if not is_inputmedia and key == inputmedia_param_name:
                pass
            elif is_inputmedia and key == inputmedia_param_name:
                files = value
            elif isinstance(value, tuple):
                files[key] = value
            elif isinstance(value, bytes):
                files[key] = value
            elif isinstance(value, dict):
                data[key] = json.dumps(value)
            elif isinstance(value, list):
                data[key] = json.dumps(value)
            else:
                data[key] = value

        # print(data, "\n", files)
        url = f'{self.__url}{method_name}'
        if run_in_thread:
            try:
                if self.__thread_pool._work_queue.qsize() >= self.__thread_pool._max_workers:
                    if not self.__hide_info:
                        _logger.info(f"[{id(self.postEverything)}] Delay run {method_name} method: until a thread pool slot is available.")

                fur = self.__thread_pool.submit(
                    self.__requestFunc, method_name, url, data, files, del_msg_after)
                fur.add_done_callback(self.__threadpool_exception)

                return True
            except Exception as e:
                _logger.error(f"Error executing method {method_name}:", str(e))
                traceback.print_exc()

                return False
        else:
            return self.__requestFunc(
                method_name=method_name,
                url=url,
                data=data,
                files=files,
                del_msg_after=del_msg_after
            )

    def __requestFunc(self, method_name, url, data, files, del_msg_after):
        try:
            with self.__session.post(url=url, data=data, files=files) as req:
                data = req.json()
                self.__debug_info(method_name, data)
                if data.get("ok", False):
                    result = data.get("result")

                    if del_msg_after >= 0:
                        if isinstance(result, dict) \
                            and "chat" in result.keys() \
                            and "id" in result.get("chat").keys() \
                            and "message_id" in result.keys():

                            chat_id = result.get("chat").get("id")
                            message_id = result.get("message_id")
                            self.__message_deletor(
                                time_gap=del_msg_after,
                                chat_id=chat_id,
                                message_id=message_id
                            )

                    return result
                else:
                    return data.get("ok")
        except Exception as e:
            _logger.error(f"Error executing method {method_name}:", str(e))
            traceback.print_exc()
            return False

    def __threadpool_exception(self, fur):
        if fur.exception() is not None:
            _logger.debug(f"EXCEPTION - {str(fur.result())}")


