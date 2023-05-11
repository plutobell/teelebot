# -*- coding:utf-8 -*-
"""
@description:基于Telegram Bot Api 的机器人框架
@creation date: 2019-08-13
@last modification: 2023-05-11
@author: Pluto (github:plutobell)
@version: 2.2.0
"""
import time
import sys
import os
import copy
import types
import string
import random
import shutil
import inspect
import importlib
import threading

from pathlib import Path
from typing import Union, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor

from .handler import _config, _bridge, _plugin_info
from .logger import _logger
from .schedule import _Schedule
from .buffer import _Buffer
from .request import _Request


class Bot(object):
    """机器人的基类"""

    def __init__(self, key: str = None, debug: bool = False, proxies: dict = None):
        config = _config()

        if key not in [None, "", " "]:
            self._key = key
            self._debug = debug
            if proxies is not None:
                self.__proxies = proxies
            else:
                self.__proxies = config["proxies"]
        else:
            self._key = config["key"]
            self._debug = config["debug"]
            self.__proxies = config["proxies"]

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
            self._secret_token = self.__make_token()
        self._offset = 0
        self._timeout = 60
        self._pool_size = config["pool_size"]
        self._buffer_size = config["buffer_size"]
        self._drop_pending_updates = config["drop_pending_updates"]
        self._updates_chat_member = config["updates_chat_member"]
        self._allowed_updates = []
        if self._updates_chat_member:
            self._allowed_updates = [
                "update_id",
                "message",
                "edited_message",
                "channel_post",
                "edited_channel_post",
                "inline_query",
                "chosen_inline_result",
                "callback_query",
                "shipping_query",
                "pre_checkout_query",
                "poll",
                "poll_answer",
                "my_chat_member",
                "chat_member",
                "chat_join_request"
            ]

        self.__root_id = config["root_id"]
        self.__bot_id = self._key.split(":")[0]
        self.__common_pkg_prefix = config["common_pkg_prefix"]
        self.__inline_mode_prefix = config["inline_mode_prefix"]
        self.__metadata_template = config["metadata_template"]
        self.__AUTHOR = config["author"]
        self.__VERSION = config["version"]
        self.__plugin_dir = config["plugin_dir"]
        self.__plugin_bridge = config["plugin_bridge"]
        self.__non_plugin_list = config["non_plugin_list"]
        self.__start_time = int(time.time())
        self.__response_times = 0
        self.__response_chats = []
        self.__response_users = []

        thread_pool_size = round(int(self._pool_size) * 2 / 3)
        schedule_queue_size = int(self._pool_size) - thread_pool_size
        self.request = _Request(thread_pool_size, self._url, self._debug, self.__proxies)
        self.schedule = _Schedule(schedule_queue_size)
        self.buffer = _Buffer(int(self._buffer_size) * 1024 * 1024,
            self.__plugin_bridge.keys(), self.__plugin_dir)

        self.__thread_pool = ThreadPoolExecutor(
            max_workers=thread_pool_size)
        self.__timer_thread_pool = ThreadPoolExecutor(
            max_workers=int(self._pool_size) * 5)

        self.__plugin_info = config["plugin_info"]
        self.__non_plugin_info = config["non_plugin_info"]

        self.__method_name = "Unknown"
        self.__plugin_info_mutex = threading.Lock()

        del config
        del thread_pool_size
        del schedule_queue_size

    def __del__(self):
        self.__thread_pool.shutdown(wait=True)
        self.__timer_thread_pool.shutdown(wait=True)
        del self.request
        del self.schedule

    def __getattr__(self, method_name):
        self.__method_name = method_name
        
        return types.MethodType(self.__method_function, self)

    def __method_function(self, *args, **kwargs):
        # command = inspect.stack()[0].function
        if len(args) != 1:
            _logger.error(f"Method '{self.__method_name}' does not accept positional arguments")

        return self.request.postEverything(self.__method_name, **kwargs)

    def __threadpool_exception(self, fur):
        """
        线程池异常回调
        """
        if fur.exception() is not None:
            _logger.debug(f"EXCEPTION - {str(fur.result())}")

    def __import_module(self, plugin_name):
        """
        动态导入模块
        """
        sys.path.append(self.path_converter(self.__plugin_dir + plugin_name + os.sep))
        Module = importlib.import_module(plugin_name)  # 模块检测

        return Module

    def __update_plugin(self, plugin_name, as_plugin=True):
        """
        热更新插件
        """

        if as_plugin:
            plugin_info = self.__plugin_info
        else:
            plugin_info = self.__non_plugin_info

        plugin_uri = self.path_converter(
            self.__plugin_dir + plugin_name + os.sep + plugin_name + ".py")
        now_mtime = os.stat(plugin_uri).st_mtime
        # print(now_mtime, self.__plugin_info[plugin_name])
        if now_mtime != plugin_info[plugin_name]:  # 插件热更新
            if os.path.exists(self.path_converter(self.__plugin_dir + plugin_name + r"/__pycache__")):
                shutil.rmtree(self.path_converter(self.__plugin_dir + plugin_name + r"/__pycache__"))
            plugin_info[plugin_name] = now_mtime
            Module = self.__import_module(plugin_name)
            importlib.reload(Module)
            _logger.info(f"The plugin {plugin_name} has been updated")

    def __load_plugin(self, now_plugin_info, as_plugin=True,
        now_plugin_bridge={}, now_non_plugin_list=[]):
        """
        动态装载插件
        """
        if as_plugin:
            for plugin in list(now_plugin_bridge.keys()): # 动态装载插件
                if plugin not in list(self.__plugin_bridge.keys()):
                    _logger.info(f"The plugin {plugin} has been installed")
                    self.__plugin_info[plugin] = now_plugin_info[plugin]
            for plugin in list(self.__plugin_bridge.keys()):
                if plugin not in list(now_plugin_bridge.keys()):
                    _logger.info(f"The plugin {plugin} has been uninstalled")
                    self.__plugin_info.pop(plugin)

                    if (self.__plugin_dir + plugin) in sys.path:
                        sys.path.remove(self.__plugin_dir + plugin)
                    if (self.__plugin_dir + plugin) in sys.modules:
                        sys.modules.pop(self.__plugin_dir + plugin)

            self.__plugin_bridge = now_plugin_bridge

            self.buffer._update(now_plugin_bridge.keys()) # Buffer动态更新

        else:
            for plugin in list(now_non_plugin_list): # 动态装载非插件包
                if plugin not in list(self.__non_plugin_list):
                    _logger.info(f"The plugin {plugin} has been installed")
                    self.__non_plugin_info[plugin] = now_plugin_info[plugin]

                    if (self.__plugin_dir + plugin) not in sys.path:
                        sys.path.append(self.__plugin_dir + plugin)

            for plugin in list(self.__non_plugin_list):
                if plugin not in list(now_non_plugin_list):
                    _logger.info(f"The plugin {plugin} has been uninstalled")
                    self.__non_plugin_info.pop(plugin)

                    if (self.__plugin_dir + plugin) in sys.path:
                        sys.path.remove(self.__plugin_dir + plugin)
                    if (self.__plugin_dir + plugin) in sys.modules:
                        sys.modules.pop(self.__plugin_dir + plugin)

            self.__non_plugin_list = now_non_plugin_list

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
        elif "query" in message.keys():
            message["message_type"] = "inline_query"
            message_type = "query"
        elif "voice_chat_started" in message.keys():
            message["message_type"] = "voice_started"
            message_type = "voice_started"
            message["voice_started"] = ""
        elif "voice_chat_ended" in message.keys():
            message["message_type"] = "voice_ended"
            message_type = "voice_ended"
            message["voice_ended"] = ""
        elif "voice_chat_participants_invited" in message.keys():
            message["message_type"] = "voice_invited"
            message_type = "voice_invited"
            message["voice_invited"] = ""
        elif "message_auto_delete_timer_changed" in message.keys():
            message["message_type"] = "message__timer_changed"
            message_type = "message__timer_changed"
            message["message__timer_changed"] = ""
        elif "my_chat_member_id" in message.keys():
            message["message_type"] = "my_chat_member_data"
            message_type = "my_chat_member_data"
            message["my_chat_member_data"] = ""
        elif "chat_member_id" in message.keys():
            message["message_type"] = "chat_member_data"
            message_type = "chat_member_data"
            message["chat_member_data"] = ""
        elif "chat_join_request_id" in message.keys():
            message["message_type"] = "chat_join_request_data"
            message_type = "chat_join_request_data"
            message["chat_join_request_data"] = ""
        elif "new_chat_members" in message.keys():
            message["message_type"] = "chat_members"
            message_type = "chat_members"
            message["chat_members"] = ""  # default prefix of command
        elif "left_chat_member" in message.keys():
            message["message_type"] = "left_member"
            message_type = "left_member"
            message["left_member"] = ""
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
        elif "contact" in message.keys():
            message["message_type"] = "contact"
            message_type = "message_type"
        elif "dice" in message.keys():
            message["message_type"] = "dice"
            message_type = "message_type"
        elif "game" in message.keys():
            message["message_type"] = "game"
            message_type = "message_type"
        elif "poll" in message.keys():
            message["message_type"] = "poll"
            message_type = "message_type"
        elif "venue" in message.keys():
            message["message_type"] = "venue"
            message_type = "message_type"
        elif "location" in message.keys():
            message["message_type"] = "location"
            message_type = "message_type"
        elif "invoice" in message.keys():
            message["message_type"] = "invoice"
            message_type = "message_type"
        elif "text" in message.keys():
            message["message_type"] = "text"
            message_type = "text"
        elif "caption" in message.keys():
            message["message_type"] = "caption"
            message_type = "caption"
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
            _logger.info(
                "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
                "User:" + user_name + "(" + str(from_id) + ") - " + \
                "Plugin: " + "" + " - " + \
                "Type:" + message["message_type"])
        else:
            _logger.info(
                "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
                "User:" + user_name + "(" + str(from_id) + ") - " + \
                "Plugin: " + str(plugin) + " - " + \
                "Type:" + message["message_type"])

    def __make_token(self, len=64):
        """
        生成指定长度的token
        """
        if len > 64:
            return "Specified length is too long."
        else:
            token = ''.join(random.sample(string.ascii_letters + string.digits + "-_", 64))
            return token

    def _pluginRun(self, bot, message):
        """
        运行插件
        """
        if message is None:
            return

        now_plugin_bridge, now_non_plugin_list = _bridge(self.__plugin_dir)
        now_plugin_info = _plugin_info(now_plugin_bridge.keys(), self.__plugin_dir)
        now_non_plugin_info = _plugin_info(now_non_plugin_list, self.__plugin_dir)

        if now_plugin_bridge != self.__plugin_bridge: # 动态装载插件
            self.__load_plugin(now_plugin_info=now_plugin_info, now_plugin_bridge=now_plugin_bridge)
        if len(now_plugin_info) != len(self.__plugin_info) or \
            now_plugin_info != self.__plugin_info: # 动态更新插件信息
            for plugin_name in list(self.__plugin_bridge.keys()):
                self.__update_plugin(plugin_name) # 热更新插件

        if now_non_plugin_list != self.__non_plugin_list: # 动态装载非插件包
            self.__load_plugin(now_plugin_info=now_non_plugin_info, as_plugin=False,
                now_non_plugin_list=now_non_plugin_list)
        if len(now_non_plugin_info) != len(self.__non_plugin_info) or \
            now_non_plugin_info != self.__non_plugin_info: # 动态更新非插件包信息
            for plugin_name in list(self.__non_plugin_list):
                self.__update_plugin(plugin_name, as_plugin=False) # 热更新非插件包

        if len(self.__plugin_bridge) == 0:
            os.system("")
            _logger.warn("\033[1;31mNo plugins installed\033[0m")

        ok, buffer_status = self.buffer.status() # 数据暂存区容量监测
        if ok and buffer_status["used"] >= buffer_status["size"]:
            os.system("")
            _logger.warn("\033[1;31mThe data buffer area is full \033[0m")

        plugin_bridge = self.__control_plugin( # pluginctl控制
            self.__plugin_bridge, message["chat"]["type"], message["chat"]["id"])

        message_type = ""
        message_type, message = self.__mark_message_for_pluginRun(message) # 分类标记消息

        if message_type == "unknown":
            self.__logging_for_pluginRun(message, "unknown")
            return

        for plugin, command in plugin_bridge.items():
            plugin_requires_version = ""
            plugin_info = self.get_plugin_info(plugin_name=plugin)
            if plugin_info["status"]:
                plugin_requires_version = plugin_info.get("metadata", {}).get("data", {}).get("Requires-teelebot", self.version)
                plugin_requires_version = plugin_requires_version.replace(">", "").replace("<", "").replace("=", "")
                if plugin_requires_version in [None, "", " "]:
                    _logger.warn(f"Skip run {plugin} plugin: failed to get the version of the plugin")
                    continue
            else:
                _logger.warn(f"Skip run {plugin} plugin: failed to get information about the plugin (error: {plugin_info['error']})")
                continue
            if plugin_requires_version > self.version:
                _logger.warn(f"Skip run {plugin} plugin: the plugin requires teelebot version >= {plugin_requires_version}")
                continue

            if message_type == "query":
                if command in ["", " ", None]:
                    continue

            if message.get(message_type)[:len(command)] == command:
                try:
                    module = self.__import_module(plugin)
                    pluginFunc = getattr(module, plugin)
                    fur = self.__thread_pool.submit(pluginFunc, bot, message)
                    fur.add_done_callback(self.__threadpool_exception)
                except Exception as e:
                    _logger.error(f"Run plugin {plugin} error: {str(e)}")

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
            elif result.get("my_chat_member"):
                query_or_message = "my_chat_member"
            elif result.get("chat_member"):
                query_or_message = "chat_member"
            elif result.get("chat_join_request"):
                query_or_message = "chat_join_request"
            elif result.get("edited_message"):
                query_or_message = "edited_message"
            elif result.get("message"):
                query_or_message = "message"
            update_ids.append(result.get("update_id"))

            if query_or_message == "inline_query":
                inline_query = result.get(query_or_message)
                inline_query["message_id"] = result["update_id"]
                inline_query["chat"] = inline_query.get("from")
                inline_query["chat"].pop("language_code")
                inline_query["chat"].pop("is_bot")
                inline_query["chat"]["type"] = "private"
                inline_query["text"] = ""
                inline_query["query"] = self.__inline_mode_prefix + inline_query["query"] # Inline Mode Plugin Prefix
                messages.append(inline_query)
            elif query_or_message == "callback_query":
                callback_query = result.get(query_or_message).get("message")
                callback_query["click_user"] = result.get(query_or_message)[
                    "from"]
                callback_query["callback_query_id"] = result.get(
                    query_or_message).get("id")
                callback_query["callback_query_data"] = result.get(
                    query_or_message).get("data")
                messages.append(callback_query)
            elif query_or_message == "my_chat_member":
                my_chat_member = result.get(query_or_message)
                my_chat_member["message_id"] = result.get("update_id")
                my_chat_member["my_chat_member_id"] = result.get("update_id")
                messages.append(my_chat_member)
            elif query_or_message == "chat_member":
                chat_member = result.get(query_or_message)
                chat_member["message_id"] = result.get("update_id")
                chat_member["chat_member_id"] = result.get("update_id")
                messages.append(chat_member)
            elif query_or_message == "chat_join_request":
                chat_join_request = result.get(query_or_message)
                chat_join_request["message_id"] = result.get("update_id")
                chat_join_request["chat_join_request_id"] = result.get("update_id")
                messages.append(chat_join_request)
            else:
                messages.append(result.get(query_or_message))

        if len(update_ids) >= 1:
            self._offset = max(update_ids) + 1
            return messages
        else:
            return None
    
    # teelebot method
    def message_deletor(self, time_gap: int, chat_id: str, message_id: str) -> str:
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

    def timer(self, time_gap: int, func: Callable[..., None], args: tuple) -> str:
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

    def path_converter(self, path: str) -> str:
        """
        根据操作系统转换URI
        """

        path = str(Path(path))

        return path
    
    def join_plugin_path(self, path: str, plugin_name: str = None) -> str:
        """
        根据提供的路径自动拼接为插件目录的URI
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]
        
        return self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}{path}")
    
    def get_plugin_info(self, plugin_name: str = None) -> dict:
        """
        获取指定插件的信息
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]
        
        if plugin_name not in list(self.plugin_bridge.keys()):
            info  = {
                "status": False,
                "error": "PluginNotFound"
            }
            return info

        command = ""
        description = ""
        buffer_permissions = "Error"
        with self.__plugin_info_mutex:
            with open(self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}__init__.py"), "r", encoding="utf-8") as init:
                lines = init.readlines()
                
                buffer_permissions_str = "False:False"
                if len(lines) >= 1:
                    command = lines[0][1:].strip()
                if len(lines) >= 2:
                    description = lines[1][1:].strip()
                if len(lines) >= 3:
                    buffer_permissions_str = lines[2][1:].strip()

                bool_true = ["True", "true"]
                bool_false = ["False", "false"]
                bool_true_and_false = ["True", "true", "False", "false"]
                buffer_permissions_list = buffer_permissions_str.split(":", 1)
                if len(buffer_permissions_list) != 2 and \
                    buffer_permissions_str not in [None, "", " "]:
                    info  = {
                        "status": False,
                        "error": "BufferPermissionsFormatError"
                    }
                    return info
                if len(buffer_permissions_list) == 2 and \
                    (buffer_permissions_list[0] not in bool_true_and_false or \
                    buffer_permissions_list[1] not in bool_true_and_false):
                    info  = {
                        "status": False,
                        "error": "BufferPermissionsFormatError"
                    }
                    return info

                if buffer_permissions_str in [None, "", " "]:
                    buffer_permissions = tuple((False, False))
                elif len(buffer_permissions_list) == 2:
                    read = buffer_permissions_list[0]
                    write = buffer_permissions_list[1]

                    if read in bool_true:
                        read = True
                    elif read in bool_false:
                        read = False
                    else:
                        read = False
                    
                    if write in bool_true:
                        write = True
                    elif write in bool_false:
                        write = False
                    else:
                        read = False

                    buffer_permissions = tuple((read, write))
        
        metadata = {}
        with self.__plugin_info_mutex:
            with open(self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}METADATA"), "r", encoding="utf-8") as meta:
                lines = meta.readlines()
                metadata_data = {}
                for line in lines:
                    line = line.strip("\n").strip(" ")
                    if line in [None, "", " "]:
                        continue
                    line_list = line.split(":", 1)
                    if len(line_list) == 2:
                        metadata_data[line_list[0].replace(" ", "")] = line_list[1].strip(" ")
                    elif len(line_list) == 1:
                        metadata_data[line_list[0].replace(" ", "")] = ""

                if not (list(metadata_data.keys()) == list(self.__metadata_template.keys())):
                    metadata = {
                        "status": False,
                        "error": "MetadataFormatError",
                        "data": {}
                    }
                else:
                    metadata = {
                        "status": True,
                        "data": metadata_data
                    }

            info  = {
                "status": True,
                "command": command,
                "description": description,
                "buffer_permissions": buffer_permissions,
                "metadata": metadata
            }

            return info

    def set_plugin_info(self, plugin_name: str = None,
                        command: str = None, description: str = None,
                        buffer_permissions: Tuple[bool, bool] = None,
                        metadata: dict = None) -> dict:
        """
        设置指定插件的信息
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]
        
        if plugin_name not in list(self.plugin_bridge.keys()):
            info  = {
                "status": False,
                "error": "PluginNotFound"
            }
            return info
        if command is None and description is None and \
            buffer_permissions is None and metadata is None:
            info  = {
                "status": True,
                "error": "Skip"
            }
            return info
        only_metadata = False
        if command is None and description is None and buffer_permissions is None:
            only_metadata = True

        status = True
        if not only_metadata:
            old_info = self.get_plugin_info(plugin_name=plugin_name)
            if not old_info["status"]:
                info  = {
                    "status": False,
                    "error": "GetOlderPluginInfoError"
                }
                return info

            if command is None:
                command = f'{old_info["command"]}'
            if description is None:
                description = f'{old_info["description"]}'
            
            buffer_permissions_str = "False:False"
            if buffer_permissions is not None:
                if not isinstance(buffer_permissions, tuple) or \
                    len(buffer_permissions) != 2 or \
                    not isinstance(buffer_permissions[0], bool) or \
                    not isinstance(buffer_permissions[0], bool):
                    info  = {
                        "status": False,
                        "error": "BufferPermissionsFormatError"
                    }
                    return info
                read = str(buffer_permissions[0])
                write = str(buffer_permissions[1])
                buffer_permissions_str = f'{read}:{write}'
            else:
                read = str(old_info["buffer_permissions"][0])
                write = str(old_info["buffer_permissions"][1])
                buffer_permissions_str = f'{read}:{write}'

            new_init_info = [
                f'#{command.strip()}\n',
                f'#{description.strip()}\n',
            ]
            try:
                with self.__plugin_info_mutex:
                    with open(self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}__init__.py"), "r", encoding="utf-8") as init:
                        lines = init.readlines()
                        if len(lines) < 2:
                            info  = {
                                "status": False,
                                "error": "InitFileFormatError"
                            }
                            return info
                        if len(lines) >= 3:
                            if buffer_permissions is not None or \
                                lines[2].strip() not in [None, "", " ", "#"]:
                                new_init_info.append(f'#{buffer_permissions_str.strip()}\n')
                            else:
                                new_init_info.append("#\n")
                        elif buffer_permissions is not None:
                            new_init_info.append(f'#{buffer_permissions_str.strip()}\n')
                        else:
                            new_init_info.append("#\n")
                        new_init_info.extend(lines[3:])
                        new_init_info[-1] = new_init_info[-1].strip()
                with self.__plugin_info_mutex:
                    with open(self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}__init__.py"), "w", encoding="utf-8") as init:
                        init.writelines(new_init_info)

                status = True
                if metadata is None:
                    info  = {
                        "status": True,
                    }
                    return info
            except Exception as e:
                print(f"Modify plugin info error: {str(e)}")
                status = False
                info  = {
                    "status": status,
                    "error": "ModifyPluginInfoError"
                }
                return info

        if status and metadata is not None:
            if not isinstance(metadata, dict):
                info  = {
                    "status": False,
                    "error": "MetadataMustBeDict"
                }
                return info
            if not (list(metadata.keys()) == list(self.__metadata_template.keys())):
                metadata = {
                    "status": False,
                    "error": "MetadataFormatError",
                }
                return info

            try:
                with self.__plugin_info_mutex:
                    with open(self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}METADATA"), "w", encoding="utf-8") as meta:
                        metadata_list = []
                        for key, value in metadata.items():
                                metadata_list.append(f"{key}: {value}\n")
                        metadata_list[-1] = metadata_list[-1].strip()
                        if metadata_list[-1].split(":")[1].strip() in [None, ""]:
                            metadata_list[-1] += " "

                        meta.writelines(metadata_list)

                        info = {
                            "status": True,
                        }
                        return info
            except Exception as e:
                print(f"Modify plugin info error: {str(e)}")
                info  = {
                    "status": False,
                    "error": "ModifyPluginInfoError"
                }
                return info
            
    def getChatCreator(self, chat_id: str) -> Union[bool, dict]:
        """
        获取群组创建者信息
        """
        if str(chat_id)[0] == "-":
            req = self.getChatAdministrators(chat_id=str(chat_id))
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

    def getChatMemberStatus(self, chat_id: str, user_id: str) -> Union[bool, str]:
        """
        获取群组用户状态
        "creator",
        "administrator",
        "member",
        "restricted",
        "left",
        "kicked"
        """
        if str(chat_id)[0] == "-":
            req = self.getChatMember(chat_id=chat_id, user_id=user_id)

            if req != False:
                return req["status"]
        else:
            return False

    def getFileDownloadPath(self, file_id: str) -> Union[bool, str]:
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

    def getChatAdminsUseridList(self, chat_id, skip_bot: bool = True,
                                privilege_users: list = None) -> Union[bool, list]:
        """
        获取聊天中的管理员user_id列表
        """
        admins = []
        results = self.getChatAdministrators(chat_id=chat_id)
        if results != False:
            for result in results:
                if skip_bot:
                    if str(result["user"]["is_bot"]) == "True":
                        continue
                admins.append(str(result["user"]["id"]))
            
            if privilege_users is not None:
                if isinstance(privilege_users, list):
                    privilege_str_users = []
                    for pu in privilege_users:
                        privilege_str_users.append(str(pu))
                    admins = list(set(admins + privilege_str_users))
                else:
                    return False

        else:
            return False

        return admins

    @property
    def plugin_bridge(self):
        """
        获取插件桥
        """

        return copy.deepcopy(self.__plugin_bridge)

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
        return copy.deepcopy(self.__response_chats)

    @property
    def response_users(self):
        """
        获取框架启动后响应的所有用户ID
        """
        return copy.deepcopy(self.__response_users)
    
    @property
    def proxies(self):
        """
        获取代理信息
        """
        return copy.deepcopy(self.__proxies)
    
    @property
    def metadata_template(self):
        """
        获取插件元素据模板
        """
        return copy.deepcopy(self.__metadata_template)


