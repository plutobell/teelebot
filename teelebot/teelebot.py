# -*- coding:utf-8 -*-
"""
@description:基于Telegram Bot Api 的机器人框架
@creation date: 2019-8-13
@last modify: 2021-03-03
@author: Pluto (github:plutobell)
@version: 1.14.5
"""
import inspect
import time
import sys
import os
import json
import shutil
import importlib
import threading

from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

from .handler import _config, _bridge, _plugin_info
from .logger import _logger
from .schedule import _Schedule
from .request import _Request


class Bot(object):
    """机器人的基类"""

    def __init__(self, key=""):
        config = _config()

        if key != "":
            self._key = key
        elif key == "":
            self._key = config["key"]

        self._cloud_api_server = config["cloud_api_server"]
        self._local_api_server = config["local_api_server"]
        if self._local_api_server != "False":
            self._basic_url = config["local_api_server"]
        else:
            self._basic_url = self._cloud_api_server
        self._url = self._basic_url + r"bot" + self._key + r"/"

        self._webhook = config["webhook"]
        if self._webhook:
            self._self_signed = config["self_signed"]
            self._cert_key = config["cert_key"]
            self._cert_pub = config["cert_pub"]
            self._server_address = config["server_address"]
            self._server_port = config["server_port"]
            self._local_address = config["local_address"]
            self._local_port = config["local_port"]
        self._offset = 0
        self._timeout = 60
        self._debug = config["debug"]
        self._pool_size = config["pool_size"]
        self._drop_pending_updates = config["drop_pending_updates"]

        self.__root_id = config["root_id"]
        self.__bot_id = self._key.split(":")[0]
        self.__AUTHOR = config["author"]
        self.__VERSION = config["version"]
        self.__plugin_dir = config["plugin_dir"]
        self.__plugin_bridge = config["plugin_bridge"]
        self.__start_time = int(time.time())
        self.__response_times = 0
        self.__response_chats = []
        self.__response_users = []

        thread_pool_size = round(int(self._pool_size) * 2 / 3)
        schedule_queue_size = int(self._pool_size) - thread_pool_size
        self.request = _Request(thread_pool_size, self._url, self._debug)
        self.schedule = _Schedule(schedule_queue_size)

        self.__thread_pool = ThreadPoolExecutor(
            max_workers=thread_pool_size)
        self.__timer_thread_pool = ThreadPoolExecutor(
            max_workers=int(self._pool_size) * 5)

        self.__plugin_info = config["plugin_info"]

        del config
        del thread_pool_size
        del schedule_queue_size

    def __del__(self):
        self.__thread_pool.shutdown(wait=True)
        self.__timer_thread_pool.shutdown(wait=True)
        del self.request
        del self.schedule

    # teelebot method
    def __threadpool_exception(self, fur):
        """
        线程池异常回调
        """
        if fur.exception() is not None:
            os.system("")
            _logger.debug("EXCEPTION" + " - " + str(fur.result()))

    def __import_module(self, plugin_name):
        """
        动态导入模块
        """
        sys.path.append(self.path_converter(self.__plugin_dir + plugin_name + os.sep))
        Module = importlib.import_module(plugin_name)  # 模块检测

        return Module

    def __update_plugin(self, plugin_name):
        """
        热更新插件
        """
        plugin_uri = self.path_converter(
            self.__plugin_dir + plugin_name + os.sep + plugin_name + ".py")
        now_mtime = os.stat(plugin_uri).st_mtime
        # print(now_mtime, self.__plugin_info[plugin_name])
        if now_mtime != self.__plugin_info[plugin_name]:  # 插件热更新
            if os.path.exists(self.path_converter(self.__plugin_dir + plugin_name + r"/__pycache__")):
                shutil.rmtree(self.path_converter(self.__plugin_dir + plugin_name + r"/__pycache__"))
            self.__plugin_info[plugin_name] = now_mtime
            Module = self.__import_module(plugin_name)
            importlib.reload(Module)
            os.system("")
            _logger.info("The plugin " + plugin_name + " has been updated")

    def __load_plugin(self, now_plugin_bridge, now_plugin_info):
        """
        动态装载插件
        """
        for plugin in list(now_plugin_bridge.keys()):
            if plugin not in list(self.__plugin_bridge.keys()):
                os.system("")
                _logger.info("The plugin " + plugin + " has been installed")
                self.__plugin_info[plugin] = now_plugin_info[plugin]
        for plugin in list(self.__plugin_bridge.keys()):
            if plugin not in list(now_plugin_bridge.keys()):
                os.system("")
                _logger.info("The plugin " + plugin + " has been uninstalled")
                self.__plugin_info.pop(plugin)

        self.__plugin_bridge = now_plugin_bridge

    def __control_plugin(self, plugin_bridge, chat_type, chat_id):
        if chat_type != "private" and "PluginCTL" in plugin_bridge.keys() \
                and plugin_bridge["PluginCTL"] == "/pluginctl":
            if os.path.exists(self.path_converter(self.__plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db")):
                with open(self.path_converter(self.__plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                    plugin_setting = f.read().strip()
                plugin_list_off = plugin_setting.split(',')
                plugin_bridge_temp = {}
                for plugin in list(plugin_bridge.keys()):
                    if plugin not in plugin_list_off:
                        plugin_bridge_temp[plugin] = plugin_bridge[plugin]
                plugin_bridge = plugin_bridge_temp

        return plugin_bridge

    def __mark_message_for_pluginRun(self, message):
        if "callback_query_id" in message.keys():  # callback query
            message["message_type"] = "callback_query_data"
            message_type = "callback_query_data"
        elif ("new_chat_members" in message.keys()) or ("left_chat_member" in message.keys()):
            message["message_type"] = "text"
            message_type = "text"
            message["text"] = ""  # default prefix of command
        elif "photo" in message.keys():
            message["message_type"] = "photo"
            message_type = "message_type"
        elif "sticker" in message.keys():
            message["message_type"] = "sticker"
            message_type = "message_type"
        elif "video" in message.keys():
            message["message_type"] = "video"
            message_type = "message_type"
        elif "audio" in message.keys():
            message["message_type"] = "audio"
            message_type = "message_type"
        elif "document" in message.keys():
            message["message_type"] = "document"
            message_type = "message_type"
        elif "text" in message.keys():
            message["message_type"] = "text"
            message_type = "text"
        elif "caption" in message.keys():
            message["message_type"] = "caption"
            message_type = "caption"
        elif "query" in message.keys():
            message["message_type"] = "query"
            message_type = "query"
        else:
            message["message_type"] = "unknown"
            message_type = "unknown"

        return message_type, message

    def __logging_for_pluginRun(self, message, plugin):
        title = ""  # INFO日志
        user_name = ""

        if message["chat"]["type"] == "private":
            if "first_name" in message["chat"].keys():
                title += message["chat"]["first_name"]
            if "last_name" in message["chat"].keys():
                if "first_name" in message["chat"].keys():
                    title += " " + message["chat"]["last_name"]
                else:
                    title += message["chat"]["last_name"]
        elif "title" in message["chat"].keys():
            title = message["chat"]["title"]
        if "reply_markup" in message.keys() and \
                message["message_type"] == "callback_query_data":
            from_id = message["click_user"]["id"]
            if "first_name" in message["click_user"].keys():
                user_name += message["click_user"]["first_name"]
            if "last_name" in message["click_user"].keys():
                if "first_name" in message["click_user"].keys():
                    user_name += " " + message["click_user"]["last_name"]
                else:
                    user_name += message["chat"]["last_name"]
        else:
            from_id = message["from"]["id"]
            if "first_name" in message["from"].keys():
                user_name += message["from"]["first_name"]
            if "last_name" in message["from"].keys():
                if "first_name" in message["from"].keys():
                    user_name += " " + message["from"]["last_name"]
                else:
                    user_name += message["from"]["last_name"]

        if message["message_type"] == "unknown":
            os.system("")
            _logger.info(
            "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
            "User:" + user_name + "(" + str(from_id) + ") - " + \
            "Plugin: " + "" + " - " + \
            "Type:" + message["message_type"])
        else:
            os.system("")
            _logger.info(
                "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
                "User:" + user_name + "(" + str(from_id) + ") - " + \
                "Plugin: " + str(plugin) + " - " + \
                "Type:" + message["message_type"])

    def _pluginRun(self, bot, message):
        """
        运行插件
        """
        if message is None:
            return

        now_plugin_bridge = _bridge(self.__plugin_dir)
        now_plugin_info = _plugin_info(now_plugin_bridge.keys(), self.__plugin_dir)

        if now_plugin_bridge != self.__plugin_bridge: # 动态装载插件
            self.__load_plugin(now_plugin_bridge, now_plugin_info)

        if len(now_plugin_info) != len(self.__plugin_info) or \
            now_plugin_info != self.__plugin_info: # 动态更新插件信息
            for plugin_name in list(self.__plugin_bridge.keys()):
                self.__update_plugin(plugin_name) #热更新插件

        if len(self.__plugin_bridge) == 0:
            os.system("")
            _logger.warn("\033[1;31mNo plugins installed\033[0m")

        plugin_bridge = self.__control_plugin( # pluginctl控制
            self.__plugin_bridge, message["chat"]["type"], message["chat"]["id"])

        message_type = ""
        message_type, message = self.__mark_message_for_pluginRun(message) # 分类标记消息

        if message_type == "unknown":
            self.__logging_for_pluginRun(message, "unknown")
            return

        for plugin, command in plugin_bridge.items():
            if message.get(message_type)[:len(command)] == command:
                module = self.__import_module(plugin)
                pluginFunc = getattr(module, plugin)
                fur = self.__thread_pool.submit(pluginFunc, bot, message)
                fur.add_done_callback(self.__threadpool_exception)

                self.__response_times += 1

                if message["chat"]["type"] != "private" and \
                message["chat"]["id"] not in self.__response_chats:
                    self.__response_chats.append(message["chat"]["id"])
                if message["from"]["id"] not in self.__response_users:
                    self.__response_users.append(message["from"]["id"])

                self.__logging_for_pluginRun(message, plugin)

    def _washUpdates(self, results):
        """
        清洗消息队列
        results应当是一个列表
        """
        if not results:
            return False
        elif len(results) < 1:
            return None
        update_ids = []
        messages = []
        for result in results:
            if "update_id" not in result.keys():
                return None
            update_ids.append(result["update_id"])
            query_or_message = ""
            if result.get("inline_query"):
                query_or_message = "inline_query"
            elif result.get("callback_query"):
                query_or_message = "callback_query"
            elif result.get("message"):
                query_or_message = "message"
            update_ids.append(result.get("update_id"))

            if query_or_message == "callback_query":
                callback_query = result.get(query_or_message).get("message")
                callback_query["click_user"] = result.get(query_or_message)[
                    "from"]
                callback_query["callback_query_id"] = result.get(
                    query_or_message).get("id")
                callback_query["callback_query_data"] = result.get(
                    query_or_message).get("data")
                messages.append(callback_query)
            else:
                messages.append(result.get(query_or_message))
        if len(update_ids) >= 1:
            self._offset = max(update_ids) + 1
            return messages
        else:
            return None

    def message_deletor(self, time_gap, chat_id, message_id):
        """
        定时删除一条消息，时间范围：[0, 900],单位秒
        """
        if time_gap < 0 or time_gap > 900:
            return "time_gap_error"
        else:
            def message_deletor_func(time_gap, chat_id, message_id):
                time.sleep(int(time_gap))
                self.deleteMessage(chat_id=chat_id, message_id=message_id)

            if time_gap == 0:
                message_deletor_func(chat_id, message_id)
            else:
                fur = self.__timer_thread_pool.submit(
                    message_deletor_func, time_gap, chat_id, message_id)
                fur.add_done_callback(self.__threadpool_exception)

            return "ok"

    def timer(self, time_gap, func, args):
        """
        单次定时器，时间范围：[0, 900],单位秒
        """
        if time_gap < 0 or time_gap > 900:
            return "time_gap_error"
        elif type(args) is not tuple:
            return "args_must_be_tuple"
        else:
            def timer_func(time_gap, func, args):
                time.sleep(int(time_gap))
                func(*args)

            if time_gap == 0:
                func(args)
            else:
                fur = self.__timer_thread_pool.submit(
                    timer_func, time_gap, func, args)
                fur.add_done_callback(self.__threadpool_exception)

            return "ok"

    def path_converter(self, path):
        """
        根据操作系统转换URI
        """

        path = str(Path(path))

        return path

    @property
    def plugin_bridge(self):
        """
        获取插件桥
        """

        return self.__plugin_bridge

    @property
    def plugin_dir(self):
        """
        获取插件路径
        """

        return self.__plugin_dir

    @property
    def version(self):
        """
        获取框架版本号
        """

        return self.__VERSION

    @property
    def author(self):
        """
        作者信息
        """

        return self.__AUTHOR

    @property
    def root_id(self):
        """
        获取root用户ID
        """

        return self.__root_id

    @property
    def bot_id(self):
        """
        获取Bot的ID
        """

        return self.__bot_id

    @property
    def uptime(self):
        """
        获取框架的持续运行时间(单位为秒)
        """
        second = int(time.time()) - self.__start_time

        return second

    @property
    def response_times(self):
        """
        获取框架启动后响应指令的统计次数
        """
        return self.__response_times

    @property
    def response_chats(self):
        """
        获取框架启动后响应的所有群组ID
        """
        return self.__response_chats

    @property
    def response_users(self):
        """
        获取框架启动后响应的所有用户ID
        """
        return self.__response_users

    def getChatCreator(self, chat_id):
        """
        获取群组创建者信息
        """
        if str(chat_id)[0] == "-":
            req = self.getChatAdministrators(str(chat_id))
            if req:
                creator = []
                for i, user in enumerate(req):
                    if user["status"] == "creator":
                        creator.append(req[i])
                if len(creator) == 1:
                    return creator[0]
                else:
                    return False
        else:
            return False

    def getFileDownloadPath(self, file_id):
        """
        生成文件下载链接
        注意：下载链接包含Bot Key
        """
        req = self.getFile(file_id=file_id)
        if req:
            file_path = req["file_path"]
            if (self._local_api_server != "False" and
                "telegram.org" not in self._basic_url):
                return file_path
            else:
                file_download_path = self._basic_url + "file/bot" + self._key + r"/" + file_path
                return file_download_path
        else:
            return False

    # Getting updates
    def getUpdates(self, limit=100, allowed_updates=None):
        """
        获取消息队列
        """
        command = inspect.stack()[0].function
        addr = command + "?offset=" + str(self._offset) + \
            "&limit=" + str(limit) + "&timeout=" + str(self._timeout)

        if allowed_updates is not None:
            return self.request.postJson(addr, allowed_updates)
        else:
            return self.request.get(addr)

    def setWebhook(self, url, certificate=None, ip_address=None,
        max_connections=None, allowed_updates=None, drop_pending_updates=None):
        """
        设置Webhook
        Ports currently supported for Webhooks: 443, 80, 88, 8443.
        """
        command = inspect.stack()[0].function
        addr = command + "?url=" + str(url)
        if ip_address is not None:
            addr += "&ip_address=" + str(ip_address)
        if max_connections is not None:
            addr += "&max_connections=" + str(max_connections)
        if allowed_updates is not None:
            addr += "&allowed_updates=" + str(allowed_updates)
        if drop_pending_updates is not None:
            addr += "&drop_pending_updates=" + str(drop_pending_updates)

        file_data = None
        if certificate is not None:
            if type(certificate) == bytes:
                file_data = {"certificate": certificate}
            else:
                file_data = {"certificate": open(certificate, 'rb')}

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def deleteWebhook(self, drop_pending_updates=None):
        """
        删除设置的Webhook
        """
        command = inspect.stack()[0].function
        addr = command
        if drop_pending_updates is not None:
            addr += "?drop_pending_updates=" + str(drop_pending_updates)
        return self.request.post(addr)

    def getWebhookInfo(self):
        """
        获取当前的Webhook状态
        """
        command = inspect.stack()[0].function
        addr = command
        return self.request.post(addr)

    # Available methods

    def getMe(self):
        """
        获取机器人基本信息
        """
        command = inspect.stack()[0].function
        addr = command + "?" + "offset=" + \
            str(self._offset) + "&timeout=" + str(self._timeout)
        return self.request.post(addr)

    def getFile(self, file_id):
        """
        获取文件信息
        """
        command = inspect.stack()[0].function
        addr = command + "?file_id=" + file_id
        return self.request.post(addr)

    def logOut(self):
        """
        在本地启动机器人之前，使用此方法从云Bot API服务器注销。
        """
        command = inspect.stack()[0].function
        addr = command

        return self.request.post(addr)

    def close(self):
        """
        在将bot实例从一个本地服务器移动到另一个本地服务器之前
        使用此方法关闭它
        """
        command = inspect.stack()[0].function
        addr = command

        return self.request.post(addr)

    def sendMessage(self, chat_id, text, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, disable_web_page_preview=None, entities=None,
        allow_sending_without_reply=None):
        """
        发送文本消息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&text=" + quote(text)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if disable_web_page_preview is not None:
            addr += "&disable_web_page_preview=" + str(disable_web_page_preview)
        if entities is not None:
            addr += "&entities=" + json.dumps(entities)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.post(addr)

    def sendVoice(self, chat_id, voice, caption=None, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None, caption_entities=None):
        """
        发送音频消息 .ogg
        """
        command = inspect.stack()[0].function
        if voice[:7] == "http://" or voice[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&voice=" + voice
        elif type(voice) == bytes:
            file_data = {"voice": voice}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(voice) == str and '.' not in voice:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&voice=" + voice
        else:
            file_data = {"voice": open(voice, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def sendAnimation(self, chat_id, animation, caption=None, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None, caption_entities=None):
        """
        发送动画 gif/mp4
        """
        command = inspect.stack()[0].function
        if animation[:7] == "http://" or animation[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&animation=" + animation
        elif type(animation) == bytes:
            file_data = {"animation": animation}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(animation) == str and '.' not in animation:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&animation=" + animation
        else:
            file_data = {"animation": open(animation, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            self.request.postFile(addr, file_data)

    def sendAudio(self, chat_id, audio, caption=None, parse_mode="Text", title=None, reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None, caption_entities=None):
        """
        发送音频 mp3
        """
        command = inspect.stack()[0].function
        if audio[:7] == "http://" or audio[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&audio=" + audio
        elif type(audio) == bytes:
            file_data = {"audio": audio}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(audio) == str and '.' not in audio:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&audio=" + audio
        else:
            file_data = {"audio": open(audio, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if title is not None:
            addr += "&title=" + title
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def sendPhoto(self, chat_id, photo, caption=None, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None, caption_entities=None):  # 发送图片
        """
        发送图片
        """
        command = inspect.stack()[0].function
        if photo[:7] == "http://" or photo[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
        elif type(photo) == bytes:
            file_data = {"photo": photo}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(photo) == str and '.' not in photo:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
        else:
            file_data = {"photo": open(photo, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def sendVideo(self, chat_id, video, caption=None, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None, caption_entities=None):
        """
        发送视频
        """
        command = inspect.stack()[0].function
        if video[:7] == "http://" or video[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video=" + video
        elif type(video) == bytes:
            file_data = {"video": video}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(video) == str and '.' not in video:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video=" + video
        else:
            file_data = {"video": open(video, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def sendVideoNote(self, chat_id, video_note, caption=None, parse_mode="Text", reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None):
        """
        发送圆形或方形视频？
        """
        command = inspect.stack()[0].function
        char_id_str = str(chat_id)
        if video_note[:7] == "http://" or video_note[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + char_id_str + "&video_note=" + video_note
        elif type(video_note) == bytes:
            file_data = {"video_note": video_note}
            addr = command + "?chat_id=" + char_id_str
        elif type(video_note) == str and '.' not in video_note:
            file_data = None
            addr = command + "?chat_id=" + char_id_str + "&video_note=" + video_note
        else:
            file_data = {"video_note": open(video_note, 'rb')}
            addr = command + "?chat_id=" + char_id_str

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def sendMediaGroup(self, chat_id, medias, disable_notification=None, reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None):  # 暂未弄懂格式。
        """
        使用此方法可以将一组照片，视频，文档或音频作为相册发送。
        文档和音频文件只能在具有相同类型消息的相册中分组。
        (目前只支持http链接和文件id，暂不支持上传文件)
        media的格式：（同时请求需要加入header头，指定传送参数为json类型，
        并且将data由字典转为json字符串传送）
        medias ={
            'caption': 'test',
            'media': [
            {
            'type': 'photo',
            'media': 'https://xxxx.com/sample/7kwx_2.jpg'
            },
            {
            'type': 'photo',
            'media': 'AgACAgQAAx0ETbyLwwADeF5s6QosSI_IW3rKir3PrMUX'
            }
            ]
        }
        InputMediaPhoto:
        type
        media
        caption
        parse_mode

        InputMediaVideo:
        type
        media
        thumb
        caption
        parse_mode
        width
        height
        duration
        supports_streaming
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.postJson(addr, medias)

    def sendDocument(self, chat_id, document, caption=None, parse_mode="Text",
        reply_to_message_id=None, reply_markup=None, disable_content_type_detection=None,
        allow_sending_without_reply=None, caption_entities=None):
        """
        发送文件
        """
        command = inspect.stack()[0].function
        if document[:7] == "http://" or document[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
        elif type(document) == bytes:
            file_data = {"document": document}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(document) == str and '.' not in document:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
        else:
            file_data = {"document": open(document, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if disable_content_type_detection is not None:
            addr += "&disable_content_type_detection=" + str(disable_content_type_detection)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def leaveChat(self, chat_id):
        """
        退出群组
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        return self.request.post(addr)

    def getChat(self, chat_id):
        """
        使用此方法可获取有关聊天的最新信息（一对一对话的用户的当前名称，
        用户的当前用户名，组或频道等）。
        成功返回一个Chat对象。
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        return self.request.post(addr)

    def getChatAdministrators(self, chat_id):
        """
        获取群组所有管理员信息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        return self.request.post(addr)

    def getChatMembersCount(self, chat_id):
        """
        获取群组成员总数
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        return self.request.post(addr)

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        """
        获取用户头像
        """
        command = inspect.stack()[0].function
        addr = command + "?user_id=" + str(user_id)

        if offset is not None:
            addr += "&offset=" + str(offset)
        if limit is not None and limit in list(range(1, 101)):
            addr += "&limit=" + str(limit)
        return self.request.post(addr)

    def getChatMember(self, chat_id, user_id):
        """
        获取群组特定用户信息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)
        return self.request.post(addr)

    def setChatTitle(self, chat_id, title):
        """
        设置群组标题
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&title=" + quote(str(title))
        return self.request.post(addr)

    def setChatDescription(self, chat_id, description):
        """
        设置群组简介（测试好像无效。。）
        //FIXME
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&description=" + quote(str(description))
        return self.request.post(addr)

    def setChatPhoto(self, chat_id, photo):
        """
        设置群组头像
        """
        command = inspect.stack()[0].function
        file_data = {"photo": open(photo, 'rb')}
        addr = command + "?chat_id=" + str(chat_id)

        return self.request.postFile(addr, file_data)

    def deleteChatPhoto(self, chat_id):
        """
        删除群组头像
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        return self.request.post(addr)

    def setChatPermissions(self, chat_id, permissions):
        """
        设置群组默认聊天权限
        permissions = {
            'can_send_messages':False,
            'can_send_media_messages':False,
            'can_send_polls':False,
            'can_send_other_messages':False,
            'can_add_web_page_previews':False,
            'can_change_info':False,
            'can_invite_users':False,
            'can_pin_messages':False
        }
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        permissions = {"permissions": permissions}

        return self.request.postJson(addr, permissions)

    def restrictChatMember(self, chat_id, user_id, permissions, until_date=None):
        """
        限制群组用户权限
        permissions = {
            'can_send_messages':False,
            'can_send_media_messages':False,
            'can_send_polls':False,
            'can_send_other_messages':False,
            'can_add_web_page_previews':False,
            'can_change_info':False,
            'can_invite_users':False,
            'can_pin_messages':False
        }
        until_date format:
        timestamp + offset
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + \
            str(chat_id) + "&user_id=" + str(user_id)
        if len(permissions) != 8:
            return False
        if until_date is not None:
            until_date = int(time.time()) + int(until_date)
            addr += "&until_date=" + str(until_date)

        return self.request.postJson(addr, permissions)

    def promoteChatMember(self, chat_id, user_id, is_anonymous=None,
        can_change_info=None, can_post_messages=None, can_edit_messages=None,
        can_delete_messages=None, can_invite_users=None, can_restrict_members=None,
        can_pin_messages=None, can_promote_members=None):
        """
        修改管理员权限(只能修改由机器人任命的管理员的权限,
        范围为机器人权限的子集)
        {
        'is_anonymous':None,
        'can_change_info':False,
        'can_post_messages':False,
        'can_edit_messages':False,
        'can_delete_messages':False,
        'can_invite_users':False,
        'can_restrict_members':False,
        'can_pin_messages':False,
        'can_promote_members':False
        }
        """
        command = inspect.stack()[0].function

        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)

        if is_anonymous is not None:
            addr += "&is_anonymous=" + str(is_anonymous)
        if can_change_info is not None:
            addr += "&can_change_info=" + str(can_change_info)
        if can_post_messages is not None:
            addr += "&can_post_messages=" + str(can_post_messages)
        if can_edit_messages is not None:
            addr += "&can_edit_messages=" + str(can_edit_messages)
        if can_delete_messages is not None:
            addr += "&can_delete_messages=" + str(can_delete_messages)
        if can_invite_users is not None:
            addr += "&can_invite_users=" + str(can_invite_users)
        if can_restrict_members is not None:
            addr += "&can_restrict_members=" + str(can_restrict_members)
        if can_pin_messages is not None:
            addr += "&can_pin_messages=" + str(can_pin_messages)
        if can_promote_members is not None:
            addr += "&can_promote_members=" + str(can_promote_members)

        return self.request.post(addr)

    def pinChatMessage(self, chat_id, message_id, disable_notification=None):
        """
        置顶消息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)

        return self.request.post(addr)

    def unpinChatMessage(self, chat_id, message_id=None):
        """
        使用此方法可以从聊天中的置顶消息列表中删除消息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)

        if message_id is not None:
            addr += "&message_id=" + str(message_id)

        return self.request.post(addr)

    def unpinAllChatMessages(self, chat_id):
        """
        使用此方法可以清除聊天中的置顶消息列表中的所有置顶消息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)

        return self.request.post(addr)

    def sendLocation(self, chat_id, latitude, longitude,
        horizontal_accuracy=None, live_period=None,
        heading=None, disable_notification=None,
        reply_to_message_id=None, reply_markup=None,
        allow_sending_without_reply=None):
        """
        发送地图定位，经纬度
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(
            float(latitude)) + "&longitude=" + str(float(longitude))
        if live_period is not None:
            addr += "&live_period=" + str(live_period)
        if horizontal_accuracy is not None:
            addr += "&horizontal_accuracy=" + str(horizontal_accuracy)
        if heading is not None:
            addr += "&heading=" + str(heading)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.post(addr)

    def sendContact(self, chat_id, phone_number, first_name, last_name=None, reply_to_message_id=None,
        reply_markup=None, allow_sending_without_reply=None):
        """
        发送联系人信息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&phone_number=" + str(phone_number) + "&first_name=" + str(
            first_name)
        if last_name is not None:
            addr += "&last_name=" + str(last_name)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.post(addr)

    def sendPoll(self, chat_id, question, options, is_anonymous=None,
        type_=None, allows_multiple_answers=None, correct_option_id=None,
        explanation=None, explanation_parse_mode=None, explanation_entities=None,
        open_period=None, close_date=None, is_closed=None, disable_notification=None,
        reply_to_message_id=None, allow_sending_without_reply=None, reply_markup=None):
        """
        使用此方法发起投票(quiz or regular, defaults to regular)
        options格式:
        options = [
            "option 1",
            "option 2"
        ]
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&question=" + str(question)
        addr += "&options=" + json.dumps(options)

        if is_anonymous is not None:
            addr += "&is_anonymous=" + str(is_anonymous)
        if type_ is not None:
            addr += "&type=" + str(type_)

        if type_ == "quiz":
            if allows_multiple_answers is not None:
                addr += "&allows_multiple_answers=" + str(allows_multiple_answers)
            if correct_option_id is not None:
                addr += "&correct_option_id=" + str(correct_option_id)
            if explanation is not None:
                addr += "&explanation=" + str(explanation)
            if explanation_parse_mode is not None:
                addr += "&explanation_parse_mode=" + str(explanation_parse_mode)
            if explanation_entities is not None:
                addr += "&explanation_entities=" + json.dumps(explanation_entities)

        if open_period is not None:
            addr += "&open_period=" + str(open_period)
        if close_date is not None:
            addr += "&close_date=" + str(close_date)
        if is_closed is not None:
            addr += "&is_closed=" + str(is_closed)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def sendDice(self, chat_id, emoji, disable_notification=None,
        reply_to_message_id=None, allow_sending_without_reply=None,
        reply_markup=None):
        """
        使用此方法发送一个动画表情
        emoji参数必须是以下几种：
            1.dice(骰子) values 1-6
            2.darts(飞镖) values 1-6
            3.basketball(篮球) values 1-5
            4.football(足球) values 1-5
            5.slot machine(老虎机) values 1-64
            默认为骰子
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&emoji=" + str(emoji)

        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def sendVenue(self, chat_id, latitude, longitude, title, address, 
        allow_sending_without_reply=None,
        foursquare_id=None, foursquare_type=None,
        google_place_id=None, google_place_type=None,
        disable_notification=None, reply_to_message_id=None,
        reply_markup=None):
        """
        使用此方法发送关于地点的信息。
        (发送地点，显示在地图上)
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(float(latitude)) + "&longitude=" + str(
            float(longitude)) + "&title=" + str(title) + "&address=" + str(address)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if foursquare_id is not None:
            addr += "&foursquare_id=" + str(foursquare_id)
        if foursquare_type is not None:
            addr += "&foursquare_type=" + str(foursquare_type)
        if google_place_id is not None:
            addr += "&google_place_id=" + str(google_place_id)
        if google_place_type is not None:
            addr += "&google_place_type=" + str(google_place_type)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)


        return self.request.post(addr)

    def sendChatAction(self, chat_id, action):
        """
        发送聊天状态，类似： 正在输入...
            typing :for text messages,
            upload_photo :for photos,
            record_video/upload_video :for videos,
            record_audio/upload_audio :for audio files,
            upload_document :for general files,
            find_location :for location data,
            record_video_note/upload_video_note :for video notes.
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&action=" + str(action)
        return self.request.post(addr)

    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        """
        转发消息
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&from_chat_id=" + str(from_chat_id) \
            + "&message_id=" + str(message_id)

        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)

        return self.request.post(addr)

    def copyMessage(self, chat_id, from_chat_id, message_id,
        caption=None, parse_mode="Text", caption_entities=None,
        disable_notification=None, reply_to_message_id=None,
        allow_sending_without_reply=None, reply_markup=None):
        """
        使用此方法可以复制任何类型的消息。
        该方法类似于forwardMessages方法,
        但是复制的消息没有指向原始消息的链接。
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&from_chat_id=" + str(from_chat_id) \
            + "&message_id=" + str(message_id)

        if caption is not None:
            addr += "&caption=" + quote(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if caption_entities is not None:
            return self.request.postJson(addr, caption_entities)
        else:
            return self.request.post(addr)


    def kickChatMember(self, chat_id, user_id, until_date=None):
        """
        从Group、Supergroup或者Channel中踢人，被踢者在until_date期限内不可再次加入
        until_date format:
        timestamp + offset
        """

        command = inspect.stack()[0].function
        if until_date is not None:
            until_date = int(time.time()) + int(until_date)
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id) + "&until_date=" + str(until_date)
        if until_date is None:
            addr = command + "?chat_id=" + \
                str(chat_id) + "&user_id=" + str(user_id)

        return self.request.post(addr)

    def unbanChatMember(self, chat_id, user_id, only_if_banned=None):
        """
        使用此方法可以取消超级组或频道中以前被踢过的用户的权限。
        (解除user被设置的until_date)
        ChatPermissions:
        can_send_messages
        can_send_media_messages
        can_send_polls
        can_send_other_messages
        can_add_web_page_previews
        can_change_info
        can_invite_users
        can_pin_messages
        """

        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + \
            str(chat_id) + "&user_id=" + str(user_id)

        if only_if_banned is not None:
            addr += "&only_if_banned=" + str(only_if_banned)

        return self.request.post(addr)

    def setChatAdministratorCustomTitle(self, chat_id, user_id, custom_title):
        """
        为群组的管理员设置自定义头衔
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id) + "&custom_title=" + quote(str(custom_title))

        return self.request.post(addr)

    def exportChatInviteLink(self, chat_id):
        """
        使用此方法生成新的群组分享链接，旧有分享链接全部失效,成功返回分享链接
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)

        return self.request.post(addr)

    def setChatStickerSet(self, chat_id, sticker_set_name):
        """
        为一个超级群组设置贴纸集
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&sticker_set_name=" + str(sticker_set_name)

        return self.request.post(addr)

    def addStickerToSet(self, user_id, name, emojis,
        png_sticker=None, tgs_sticker=None, mask_position=None):
        """
        使用此方法在机器人创建的集合中添加一个新贴纸。
        必须使用png标签或tgs标签中的一个字段。
        动画贴纸只能添加到动画贴纸组中。
        动画贴纸组最多可以有50个贴纸。
        静态贴纸组最多可以有120个贴纸。
        """
        command = inspect.stack()[0].function
        addr = command + "?user_id=" + str(user_id) + "&name=" + str(name) \
            + "&emoji=" + str(emoji)

        if png_sticker is not None and tgs_sticker is not None:
            return False
        elif png_sticker is None and tgs_sticker is None:
            return False
        else:
            if png_sticker is not None:
                if png_sticker[:7] == "http://" or png_sticker[:7] == "https:/":
                    file_data = None
                    addr = command + "?chat_id=" + str(chat_id) + "&png_sticker=" + png_sticker
                elif type(png_sticker) == bytes:
                    file_data = {"png_sticker": png_sticker}
                    addr = command + "?chat_id=" + str(chat_id)
                elif type(png_sticker) == str and '.' not in png_sticker:
                    file_data = None
                    addr = command + "?chat_id=" + str(chat_id) + "&png_sticker=" + png_sticker
                else:
                    file_data = {"png_sticker": open(png_sticker, 'rb')}
                    addr = command + "?chat_id=" + str(chat_id)
            elif tgs_sticker is not None:
                if tgs_sticker[:7] == "http://" or tgs_sticker[:7] == "https:/":
                    file_data = None
                    addr = command + "?chat_id=" + str(chat_id) + "&tgs_sticker=" + tgs_sticker
                elif type(png_sticker) == bytes:
                    file_data = {"tgs_sticker": tgs_sticker}
                    addr = command + "?chat_id=" + str(chat_id)
                elif type(tgs_sticker) == str and '.' not in tgs_sticker:
                    file_data = None
                    addr = command + "?chat_id=" + str(chat_id) + "&tgs_sticker=" + tgs_sticker
                else:
                    file_data = {"tgs_sticker": open(tgs_sticker, 'rb')}
                    addr = command + "?chat_id=" + str(chat_id)

            if file_data is None:
                return self.request.post(addr)
            else:
                return self.request.postFile(addr, file_data)

    def deleteChatStickerSet(self, chat_id):
        """
        删除超级群组的贴纸集
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)

        return self.request.post(addr)

    def editMessageLiveLocation(self, latitude, longitude,
        horizontal_accuracy=None, chat_id=None, message_id=None,
        heading=None, inline_message_id=None, reply_markup=None):
        """
        使用此方法编辑实时位置消息
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function

        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        addr += "&latitude=" + str(latitude)
        addr += "&longitude=" + str(longitude)

        if horizontal_accuracy is not None:
            addr += "&horizontal_accuracy="  + str(horizontal_accuracy)
        if heading is not None:
            addr += "&heading=" + str(heading)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def stopMessageLiveLocation(self, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        """
        使用此方法可在活动期间到期前停止更新活动位置消息
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function

        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def setMyCommands(self, commands):
        """
        使用此方法更改机器人的命令列表
        commands传入格式示例：
        commands = [
            {"command": "start", "description": "插件列表"},
            {"command": "bing", "description": "获取每日Bing壁纸"}
        ]
        """
        command = inspect.stack()[0].function
        addr = command
        commands = {"commands": commands}

        return self.request.postJson(addr, commands)

    def getMyCommands(self):
        """
        使用此方法获取机器人当前的命令列表
        """
        command = inspect.stack()[0].function
        addr = command

        return self.request.post(addr)

    # Updating messages
    def editMessageText(self, text, chat_id=None, message_id=None, inline_message_id=None,
        parse_mode="Text", disable_web_page_preview=None,
        reply_markup=None, entities=None):
        """
        编辑一条文本消息.成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function

        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        addr += "&text=" + quote(str(text))
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + str(parse_mode)
        if disable_web_page_preview is not None:
            addr += "&disable_web_page_preview=" + \
                    str(disable_web_page_preview)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if entities is not None:
            addr += "&entities=" + json.dumps(entities)

        return self.request.post(addr)

    def editMessageCaption(self, chat_id=None, message_id=None,
        inline_message_id=None, caption=None, parse_mode="Text",
        reply_markup=None, caption_entities=None):
        """
        编辑消息的Caption。成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function
        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if caption is not None:
            addr += "&caption=" + quote(str(caption))
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + str(parse_mode)
        if reply_markup is not None:
            addr += "&reply_markup=" + str(reply_markup)
        if caption_entities is not None:
            addr += "&caption_entities=" + json.dumps(caption_entities)

        return self.request.post(addr)

    def editMessageMedia(self, media, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        """
        编辑消息媒体
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        media format:
        media = {
            'media':{
                    'type': 'photo',
                    'media': 'http://pic1.win4000.com/pic/d/6a/25a2c0e959.jpg',
                    'caption': '编辑后的Media'
            }
        }
        """
        command = inspect.stack()[0].function
        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.postJson(addr, media)

    def editMessageReplyMarkup(self, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        """
        编辑MessageReplyMarkup
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function
        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def stopPoll(self, chat_id, message_id, reply_markup=None):
        """
        停止投票？并返回最终结果
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)

        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        return self.request.post(addr)

    def deleteMessage(self, chat_id, message_id):
        """
        删除一条消息，机器人必须具备恰当的权限
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)

        return self.request.post(addr)

    # Inline mode

    def answerInlineQuery(self, inline_query_id, results, cache_time=None,
        is_personal=None, next_offset=None, switch_pm_text=None, switch_pm_parameter=None):
        """
        使用此方法发送Inline mode的应答
        """
        command = inspect.stack()[0].function
        addr = command + "?inline_query_id=" + str(inline_query_id)
        if cache_time is not None:
            addr += "&cache_time=" + str(cache_time)
        if is_personal is not None:
            addr += "&is_personal=" + str(is_personal)
        if next_offset is not None:
            addr += "&next_offset=" + str(next_offset)
        if switch_pm_text is not None:
            addr += "&switch_pm_text=" + str(switch_pm_text)
        if switch_pm_parameter is not None:
            addr += "&switch_pm_parameter=" + str(switch_pm_parameter)

        return self.request.postJson(addr, results)

    def answerCallbackQuery(self, callback_query_id, text=None, show_alert="false", url=None, cache_time=0):
        """
        使用此方法发送CallbackQuery的应答
        InlineKeyboardMarkup格式:
        replyKeyboard = [
        [
            {  "text": "命令菜单","callback_data":"/start"},
            {  "text": "一排之二","url":"https://google.com"}
        ],
        [
            { "text": "二排之一","url":"https://google.com"},
            { "text": "二排之二","url":"https://google.com"},
            { "text": "二排之三","url":"https://google.com"}
        ]
        ]
        reply_markup = {
            "inline_keyboard": replyKeyboard
        }
        ReplyKeyboardMarkup格式(似乎不能用于群组):
        replyKeyboard = [
        [
            {  "text": "命令菜单"},
            {  "text": "一排之二"}
        ],
        [
            { "text": "二排之一"},
            { "text": "二排之二"},
            { "text": "二排之三"}
        ]
        ]
        reply_markup = {
        "keyboard": replyKeyboard,
        "resize_keyboard": bool("false"),
        "one_time_keyboard": bool("false"),
        "selective": bool("true")
        }
        ReplyKeyboardRemove格式:
        reply_markup = {
        "remove_keyboard": bool("true"),
        "selective": bool("true")
        }
        """
        command = inspect.stack()[0].function
        addr = command + "?callback_query_id=" + str(callback_query_id)
        if text is not None:
            addr += "&text=" + quote(str(text))
        if show_alert == "true":
            addr += "&show_alert=" + str(bool(show_alert))
        if url is not None:
            addr += "&url=" + str(url)
        if cache_time != 0:
            addr += "&cache_time=" + str(cache_time)

        return self.request.post(addr)

    # Stickers
    def sendSticker(self, chat_id, sticker, disable_notification=None,
        reply_to_message_id=None, reply_markup=None,
        allow_sending_without_reply=None):
        """
        使用此方法发送静态、webp或动画、tgs贴纸
        """
        command = inspect.stack()[0].function

        if sticker[:7] == "http://" or sticker[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&sticker=" + sticker
        elif type(sticker) == bytes:
            file_data = {"sticker": sticker}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(sticker) == str and '.' not in sticker:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&sticker=" + sticker
        else:
            file_data = {"sticker": open(sticker, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def getStickerSet(self, name):
        """
        使用此方法获取贴纸集
        """
        command = inspect.stack()[0].function
        addr = command + "?name=" + str(name)

        return self.request.post(addr)

    def uploadStickerFile(self, user_id, name, title, emojis,
        png_sticker=None, tgs_sticker=None, contains_masks=None,
        mask_position=None):
        """
        使用此方法可以上传带有标签的.PNG文件
        以供以后在createNewStickerSet和addStickerToSet方法中使用
        （可以多次使用）
        """
        command = inspect.stack()[0].function

        user_id_str = str(user_id)
        if png_sticker[:7] == "http://" or png_sticker[:7] == "https:/":
            file_data = None
            addr = command + "?user_id=" + user_id_str + "&png_sticker=" + png_sticker
        elif type(png_sticker) == bytes:
            file_data = {"png_sticker": png_sticker}
            addr = command + "?user_id=" + user_id_str
        elif type(png_sticker) == str and '.' not in png_sticker:
            file_data = None
            addr = command + "?user_id=" + user_id_str + "&png_sticker=" + png_sticker
        else:
            file_data = {"png_sticker": open(png_sticker, 'rb')}
            addr = command + "?user_id=" + user_id_str

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    def createNewStickerSet(self, user_id, name, title, emojis, png_sticker=None, tgs_sticker=None,
        contains_masks=None, mask_position=None):
        """
        使用此方法可以创建用户拥有的新贴纸集
        机器人将能够编辑由此创建的贴纸集
        png_sticker或tgs_sticker字段只能且必须存在一个
        """
        command = inspect.stack()[0].function
        addr = command + "?user_id=" + str(user_id)
        addr += "&name=" + str(name)
        addr += "&title=" + str(title)
        addr += "&emojis=" + str(emojis)

        if png_sticker is None and tgs_sticker is None:
            return False
        elif png_sticker is not None and tgs_sticker is not None:
            return False
        else:
            if png_sticker is not None:
                if png_sticker[:7] == "http://" or png_sticker[:7] == "https:/":
                    file_data = None
                    addr += "&png_sticker=" + png_sticker
                elif type(png_sticker) == bytes:
                    file_data = {"png_sticker": png_sticker}
                elif type(png_sticker) == str and '.' not in png_sticker:
                    file_data = None
                    addr += "&png_sticker=" + png_sticker
                else:
                    file_data = {"png_sticker": open(png_sticker, 'rb')}
            elif tgs_sticker is not None:
                if tgs_sticker[:7] == "http://" or tgs_sticker[:7] == "https:/":
                    file_data = None
                    addr += "&tgs_sticker=" + tgs_sticker
                elif type(tgs_sticker) == bytes:
                    file_data = {"tgs_sticker": tgs_sticker}
                elif type(tgs_sticker) == str and '.' not in tgs_sticker:
                    file_data = None
                    addr += "&tgs_sticker=" + tgs_sticker
                else:
                    file_data = {"tgs_sticker": open(tgs_sticker, 'rb')}

            if contains_masks is not None:
                addr += "&contains_masks=" + str(contains_masks)
                if mask_position is not None:
                    addr += "&mask_position=" + json.dumps(mask_position)
                else:
                    return False

            if file_data is None:
                return self.request.post(addr)
            else:
                return self.request.postFile(addr, file_data)

    def addStickerToSet(self, user_id, name, emojis, png_sticker=None, tgs_sticker=None,
        mask_position=None):
        """
        使用此方法可以将新标签添加到由机器人创建的集合中
        png_sticker或tgs_sticker字段只能且必须存在一个。
        可以将动画贴纸添加到动画贴纸集中，并且只能添加到它们
        动画贴纸集最多可以包含50个贴纸。 静态贴纸集最多可包含120个贴纸
        """
        command = inspect.stack()[0].function
        addr = command + "?user_id=" + str(user_id)
        addr += "&name=" + str(name)
        addr += "&emojis=" + str(emojis)

        if png_sticker is None and tgs_sticker is None:
            return False
        elif png_sticker is not None and tgs_sticker is not None:
            return False
        else:
            if png_sticker is not None:
                if png_sticker[:7] == "http://" or png_sticker[:7] == "https:/":
                    file_data = None
                    addr += "&png_sticker=" + png_sticker
                elif type(png_sticker) == bytes:
                    file_data = {"png_sticker": png_sticker}
                elif type(png_sticker) == str and '.' not in png_sticker:
                    file_data = None
                    addr += "&png_sticker=" + png_sticker
                else:
                    file_data = {"png_sticker": open(png_sticker, 'rb')}
            elif tgs_sticker is not None:
                if tgs_sticker[:7] == "http://" or tgs_sticker[:7] == "https:/":
                    file_data = None
                    addr += "&tgs_sticker=" + tgs_sticker
                elif type(tgs_sticker) == bytes:
                    file_data = {"tgs_sticker": tgs_sticker}
                elif type(tgs_sticker) == str and '.' not in tgs_sticker:
                    file_data = None
                    addr += "&tgs_sticker=" + tgs_sticker
                else:
                    file_data = {"tgs_sticker": open(tgs_sticker, 'rb')}

            if mask_position is not None:
                addr += "&mask_position=" + json.dumps(mask_position)

            if file_data is None:
                return self.request.post(addr)
            else:
                return self.request.postFile(addr, file_data)

    def setStickerPositionInSet(self, sticker, position):
        """
        使用此方法将机器人创建的一组贴纸移动到特定位置
        """
        command = inspect.stack()[0].function
        addr = command + "?sticker=" + str(sticker)
        addr += "&position=" + str(position)

        return self.request.post(addr)

    def deleteStickerFromSet(self, sticker):
        """
        使用此方法从机器人创建的集合中删除贴纸
        """
        command = inspect.stack()[0].function
        addr = command + "?sticker=" + str(sticker)

        return self.request.post(addr)

    def setStickerSetThumb(self, name, user_id, thumb=None):
        """
        使用此方法设置贴纸集的缩略图
        只能为动画贴纸集设置动画缩略图
        """
        command = inspect.stack()[0].function
        addr = command + "?name=" + str(name)
        addr += "&user_id=" + str(user_id)

        if thumb is not None:
            if thumb[:7] == "http://" or thumb[:7] == "https:/":
                file_data = None
                addr += "&thumb=" + thumb
            elif type(thumb) == bytes:
                file_data = {"thumb": thumb}
            elif type(thumb) == str and '.' not in thumb:
                file_data = None
                addr += "&thumb=" + thumb
            else:
                file_data = {"thumb": open(thumb, 'rb')}

        if file_data is None:
            return self.request.post(addr)
        else:
            return self.request.postFile(addr, file_data)

    # Payments
    def sendInvoice(self, chat_id, title, description, payload, provider_token, start_parameter,
                    currency, prices, provider_data=None, photo_url=None,
                    photo_size=None, photo_width=None, photo_height=None,
                    need_name=None, need_phone_number=None, need_email=None,
                    need_shipping_address=None, send_phone_number_to_provider=None,
                    send_email_to_provider=None, is_flexible=None, disable_notification=None,
                    reply_to_message_id=None, reply_markup=None,
                    allow_sending_without_reply=None):
        """
        使用此方法发送发票
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        addr += "&title=" + str(title)
        addr += "&description=" + str(description)
        addr += "&payload" + str(payload)
        addr += "&provider_token=" + str(provider_token)
        addr += "&start_parameter=" + str(start_parameter)
        addr += "&currency=" + str(currency)
        addr += "&prices=" + json.dumps(prices)

        if provider_data is not None:
            addr += "&provider_data=" + str(provider_data)
        if photo_url is not None:
            addr += "&photo_url=" + str(photo_url)
        if photo_size is not None:
            addr += "&photo_size=" + str(photo_size)
        if photo_width is not None:
            addr += "&photo_width=" + str(photo_width)
        if photo_height is not None:
            addr += "&photo_height=" + str(photo_height)
        if need_name is not None:
            addr += "&need_name=" + str(need_name)
        if need_phone_number is not None:
            addr += "&need_phone_number=" + str(need_phone_number)
        if need_email is not None:
            addr += "&need_email=" + str(need_email)
        if need_shipping_address is not None:
            addr += "&need_shipping_address=" + str(need_shipping_address)
        if send_phone_number_to_provider is not None:
            addr += "&send_phone_number_to_provider=" + \
                    str(send_phone_number_to_provider)
        if send_email_to_provider is not None:
            addr += "&send_email_to_provider=" + str(send_email_to_provider)
        if is_flexible is not None:
            addr += "&is_flexible=" + str(is_flexible)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.post(addr)

    def answerShippingQuery(self, shipping_query_id, ok, shipping_options=None, error_message=None):
        """
        使用此方法可以答复运输查询
        """
        command = inspect.stack()[0].function
        addr = command + "?shipping_query_id=" + str(shipping_query_id)
        addr += "&ok=" + str(ok)

        if shipping_options is not None:
            addr += "&shipping_options=" + json.dumps(shipping_options)
        if error_message is not None:
            addr += "&error_message=" + str(error_message)

        return self.request.post(addr)

    def answerPreCheckoutQuery(self, pre_checkout_query_id, ok, error_message=None):
        """
        使用此方法来响应此类预结帐查询
        """
        command = inspect.stack()[0].function
        addr = command + "?pre_checkout_query_id=" + str(pre_checkout_query_id)
        addr += "&ok=" + str(ok)

        if error_message is not None:
            addr += "&error_message=" + str(error_message)

        return self.request.post(addr)

    # Telegram Passport

    def setPassportDataErrors(self, user_id, errors):
        """
        通知用户他们提供的某些Telegram Passport元素包含错误
        在错误纠正之前，用户将无法重新提交其护照
        （错误返回字段的内容必须更改）
        """
        command = inspect.stack()[0].function
        addr = command + "?user_id=" + str(user_id)
        addr += "&errors=" + json.dumps(errors)

        return self.request.post(addr)

    # Games

    def sendGame(self, chat_id, game_short_name, disable_notification=None,
        reply_to_message_id=None, reply_markup=None,
        allow_sending_without_reply=None):
        """
        使用此方法发送游戏
        """
        command = inspect.stack()[0].function
        addr = command + "?chat_id=" + str(chat_id)
        addr += "&game_short_name=" + str(game_short_name)

        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup is not None:
            addr += "&reply_markup=" + json.dumps(reply_markup)
        if allow_sending_without_reply is not None:
            addr += "&allow_sending_without_reply=" + str(allow_sending_without_reply)

        return self.request.post(addr)

    def setGameScore(self, user_id, score, force=None, disable_edit_message=None,
                    chat_id=None, message_id=None, inline_message_id=None):
        """
        使用此方法设置游戏中指定用户的分数
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function

        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        addr += "&user_id=" + str(user_id)
        addr += "&score=" + str(score)

        if force is not None:
            addr += "&force=" + str(force)
        if disable_edit_message is not None:
            addr += "&disable_edit_message=" + str(disable_edit_message)

        return self.request.post(addr)

    def getGameHighScores(self, user_id, chat_id=None, message_id=None, inline_message_id=None):
        """
        使用此方法获取高分表的数据
        将返回指定用户及其在游戏中几个邻居的分数
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        """
        command = inspect.stack()[0].function

        if inline_message_id is None:
            if message_id is None or chat_id is None:
                return False

        if inline_message_id is not None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        addr += "&user_id=" + str(user_id)

        return self.request.post(addr)
