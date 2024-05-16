# -*- coding:utf-8 -*-
"""
@description: A Python-based Telegram Bot framework
@creation date: 2019-08-13
@last modification: 2024-05-16
@author: Pluto (github:plutobell)
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
import traceback
import threading
import importlib
import functools

from pathlib import Path
from typing import Union, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from .handler import _config, _bridge, _plugin_info
from .logger import _logger
from .schedule import _Schedule
from .buffer import _Buffer
from .request import _Request
from .metadata import _Metadata
from .common import (
    __plugin_init_func_name__,
    __plugin_control_plugin_name__,
    __plugin_control_plugin_command__
    )


class Bot(object):
    """
    Bot Class
    """

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
        self._url = f'{self._basic_url}bot{self._key}/'

        self._webhook = config["webhook"]
        if self._webhook:
            self._self_signed = config["self_signed"]
            self._cert_key = config["cert_key"]
            self._cert_pub = config["cert_pub"]
            self._load_cert = config["load_cert"]
            self._server_address = config["server_address"]
            self._server_port = config["server_port"]
            self._local_address = config["local_address"]
            self._local_port = config["local_port"]
            if "secret_token" in list(config.keys()):
                if config["secret_token"] not in [None, "", " "]:
                    self._secret_token = config["secret_token"]
                else:
                    self._secret_token = self.__make_token()
            else:
                self._secret_token = self.__make_token()
        self._offset = 0
        self._timeout = 0
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
        try:
            self.__bot_id = self._key.split(":")[0]
        except:
            self.__bot_id = ""
        self.__common_pkg_prefix = config["common_pkg_prefix"]
        self.__inline_mode_prefix = config["inline_mode_prefix"]
        self.__AUTHOR = config["author"]
        self.__VERSION = config["version"]
        self.__plugin_dir = config["plugin_dir"]
        self.__plugin_bridge = config["plugin_bridge"]
        self.__non_plugin_list = config["non_plugin_list"]
        self.__start_time = int(time.time())
        self.__response_times = 0
        self.__response_chats = []
        self.__response_users = []

        thread_pool_size = int(self._pool_size)
        if int(self._pool_size) >= 3:
            thread_pool_size = round(int(self._pool_size) * 2 / 3)
        schedule_queue_size = round(int(self._pool_size) - thread_pool_size)
        if schedule_queue_size == 0: schedule_queue_size = int(self._pool_size)

        self.request = _Request(
            thread_pool_size, self._url, self.message_deletor, config["hide_info"], self._debug, self.__proxies)
        self.schedule = _Schedule(schedule_queue_size)
        self.buffer = _Buffer(int(self._buffer_size) * 1024 * 1024,
            self.__plugin_bridge.keys(), self.__plugin_dir)
        self.metadata = _Metadata(self.__plugin_dir)

        self.__thread_pool = ThreadPoolExecutor(
            max_workers=thread_pool_size)
        self.__timer_thread_pool = ThreadPoolExecutor(
            max_workers=int(self._pool_size) * 5)
        plugin_init_pool_size = int(self._pool_size)
        if int(self._pool_size) >= 3:
            plugin_init_pool_size = round(int(self._pool_size) / 3)
        self.__plugin_init_pool = ThreadPoolExecutor(
            max_workers=plugin_init_pool_size)

        self.__plugin_info = config["plugin_info"]
        self.__non_plugin_info = config["non_plugin_info"]

        self.__method_name = ""
        self.__hide_info = config["hide_info"]

        self.__plugins_init_status_mutex = threading.RLock()
        self.__plugins_init_status = {}
        self.__plugin_init_furs_mutex = threading.RLock()
        self.__plugin_init_furs = {}

        del config
        del schedule_queue_size
        del plugin_init_pool_size

    def __del__(self):
        self.__thread_pool.shutdown(wait=True)
        self.__timer_thread_pool.shutdown(wait=True)
        self.__plugin_init_pool.shutdown(wait=True)
        del self.request
        del self.schedule
        del self.buffer
        del self.metadata
        del self.__plugins_init_status
        del self.__plugin_init_furs

    def __getattr__(self, method_name):
        self.__method_name = method_name
        
        return types.MethodType(self.__method_function, self)

    def __method_function(self, *args, **kwargs):
        # command = inspect.stack()[0].function
        if len(args) != 1:
            _logger.error(f"Method '{self.__method_name}' does not accept positional arguments")
            raise MethodPositionalArgumentError("Method does not accept positional arguments")

        return self.request.postEverything(self.__method_name, **kwargs)

    def __threadpool_exception(self, fur):
        """
        Thread pool exception callback
        """
        if fur.exception() is not None:
            _logger.debug(f"EXCEPTION - {str(fur.result())}")

    def _plugins_init(self, bot):
        """
        Execute the init func of the plugins
        """      
        for plugin, _ in self.__plugin_bridge.items():
            try:
                with self.__plugins_init_status_mutex:
                    if plugin not in list(self.__plugins_init_status.keys()):
                        continue
                    elif self.__plugins_init_status[plugin] == True:
                        continue
                    elif self.__plugins_init_status[plugin] == False:
                        with self.__plugin_init_furs_mutex:
                            if isinstance(self.__plugin_init_furs[plugin], Future):
                                if self.__plugin_init_furs[plugin].running():
                                    _logger.warn(f"The plugin {plugin} is still initializing...")
                                elif not self.__plugin_init_furs[plugin].done():
                                    if not self.__hide_info:
                                        _logger.info(f"Delay initialize {plugin} plugin: until a thread pool slot is available.")
                                continue

                module = self.__import_module(plugin)
                pluginInitFunc = getattr(module, __plugin_init_func_name__, None)

                if pluginInitFunc != None:
                    def __threadpool_exception(fur, plugin_name, status=False):
                        if fur.exception() is not None:
                            _logger.error(f"The plugin {plugin} initialization error.")
                            _logger.debug(f"EXCEPTION - {str(fur.result())}")
                        else:
                            self.__update_plugin_init_status(plugin_name=plugin_name, status=status)
                            if not self.__hide_info:
                                _logger.info(f"The plugin {plugin_name} initialization completed.")

                    if self.__plugin_init_pool._work_queue.qsize() >= self.__plugin_init_pool._max_workers:
                        if not self.__hide_info:
                            _logger.info(f"Delay initialize {plugin} plugin: until a thread pool slot is available.")

                    fur = self.__plugin_init_pool.submit(pluginInitFunc, bot)
                    callback_with_args = functools.partial(__threadpool_exception, plugin_name=plugin, status=True)
                    fur.add_done_callback(callback_with_args)

                    with self.__plugin_init_furs_mutex:
                        if plugin in list(self.__plugin_init_furs.keys()):
                            if isinstance(self.__plugin_init_furs[plugin], Future):
                                if not self.__plugin_init_furs[plugin].done():
                                    self.__plugin_init_furs[plugin].cancel()
                            self.__plugin_init_furs[plugin] = fur

            except Exception as e:
                _logger.error(f"Failed to initialize plugin {plugin}: {str(e)}")
                traceback.print_exc()

    def _update_plugins_init_status(self):
        """
        Update plugins init status
        """
        new_status_dict = {}

        with self.__plugins_init_status_mutex:
            for plugin, _ in self.__plugin_bridge.items():
                with self.__plugins_init_status_mutex:
                    if plugin in list(self.__plugins_init_status.keys()):
                        new_status_dict[plugin] = self.__plugins_init_status[plugin]
                    else:
                        new_status_dict[plugin] = False

            self.__plugins_init_status = new_status_dict

        new_plugin_init_furs_dict = {}
        with self.__plugin_init_furs_mutex:
            merge_plugin_list = list(set(list(self.__plugin_bridge.keys()) + list(self.__plugin_init_furs.keys())))
            for plugin in merge_plugin_list:
                new_plugin_init_furs_dict[plugin] = None
                if plugin in list(self.__plugin_init_furs.keys()):
                    if isinstance(self.__plugin_init_furs[plugin], Future):
                        if not self.__plugin_init_furs[plugin].done():
                            new_plugin_init_furs_dict[plugin] = self.__plugin_init_furs[plugin]

            self.__plugin_init_furs = new_plugin_init_furs_dict

    def __update_plugin_init_status(self, plugin_name, status=False):
        """
        Update plugin init status by plugin_name
        """
        with self.__plugins_init_status_mutex:
            if plugin_name in list(self.__plugins_init_status.keys()):
                self.__plugins_init_status[plugin_name] = status
                if not status:
                    with self.__plugin_init_furs_mutex:
                        if isinstance(self.__plugin_init_furs[plugin_name], Future):
                            if not self.__plugin_init_furs[plugin_name].done():
                                self.__plugin_init_furs[plugin_name].cancel()

    def __import_module(self, plugin_name):
        """
        Dynamic import module
        """
        if self.__plugin_dir not in sys.path:
            sys.path.append(self.__plugin_dir)
        # print(sys.path)

        Module = importlib.import_module(f'{plugin_name}.{plugin_name}')  # Module Detection

        return Module

    def __update_plugin(self, plugin_name, as_plugin=True):
        """
        Hot update plugin
        """

        try:
            if as_plugin:
                plugin_info = self.__plugin_info
            else:
                plugin_info = self.__non_plugin_info

            plugin_uri = self.path_converter(
                f'{self.__plugin_dir}{plugin_name}{os.sep}{plugin_name}.py')
            now_mtime = os.stat(plugin_uri).st_mtime
            # print(now_mtime, self.__plugin_info[plugin_name])
            if now_mtime != plugin_info[plugin_name]:  # Plugin hot update
                if os.path.exists(self.path_converter(f'{self.__plugin_dir}{plugin_name}{os.sep}__pycache__')):
                    shutil.rmtree(self.path_converter(f'{self.__plugin_dir}{plugin_name}{os.sep}__pycache__'))
                plugin_info[plugin_name] = now_mtime

                Module = self.__import_module(plugin_name)
                importlib.reload(Module)

                self.__update_plugin_init_status(plugin_name=plugin_name, status=False)
                if not self.__hide_info:
                    _logger.info(f"The plugin {plugin_name} has been updated.")

        except Exception as e:
            _logger.error(f"Failed to update plugin {plugin_name}: {str(e)}")
            traceback.print_exc()

    def __load_plugin(self, now_plugin_info, as_plugin=True,
        now_plugin_bridge={}, now_non_plugin_list=[]):
        """
        Dynamic loading plugin
        """
        if as_plugin:
            for plugin in list(now_plugin_bridge.keys()): # Dynamic Loading Plugin
                if plugin not in list(self.__plugin_bridge.keys()):
                    if not self.__hide_info:
                        _logger.info(f"The plugin {plugin} has been installed.")
                    self.__plugin_info[plugin] = now_plugin_info[plugin]
            for plugin in list(self.__plugin_bridge.keys()):
                if plugin not in list(now_plugin_bridge.keys()):
                    if not self.__hide_info:
                        _logger.info(f"The plugin {plugin} has been uninstalled.")
                    self.__plugin_info.pop(plugin)

                    if (f'{self.__plugin_dir}{plugin}') in sys.path:
                        sys.path.remove(f'{self.__plugin_dir}{plugin}')
                    if (f'{self.__plugin_dir}{plugin}') in sys.modules:
                        sys.modules.pop(f'{self.__plugin_dir}{plugin}')

            self.__plugin_bridge = now_plugin_bridge

            self.buffer._update(now_plugin_bridge.keys()) # Dynamic Update Buffer

        else:
            for plugin in list(now_non_plugin_list): # Dynamically loading non-plugin packages
                if plugin not in list(self.__non_plugin_list):
                    if not self.__hide_info:
                        _logger.info(f"The plugin {plugin} has been installed")
                    self.__non_plugin_info[plugin] = now_plugin_info[plugin]

                    if (f'{self.__plugin_dir}{plugin}') not in sys.path:
                        sys.path.append(f'{self.__plugin_dir}{plugin}')

            for plugin in list(self.__non_plugin_list):
                if plugin not in list(now_non_plugin_list):
                    if not self.__hide_info:
                        _logger.info(f"The plugin {plugin} has been uninstalled")
                    self.__non_plugin_info.pop(plugin)

                    if (f'{self.__plugin_dir}{plugin}') in sys.path:
                        sys.path.remove(f'{self.__plugin_dir}{plugin}')
                    if (f'{self.__plugin_dir}{plugin}') in sys.modules:
                        sys.modules.pop(f'{self.__plugin_dir}{plugin}')

            self.__non_plugin_list = now_non_plugin_list

    def __control_plugin(self, plugin_bridge, chat_type, chat_id):
        control_plugin = __plugin_control_plugin_name__
        control_plugin_command = __plugin_control_plugin_command__

        if chat_type != "private" and control_plugin in plugin_bridge.keys() \
                and plugin_bridge[control_plugin] == control_plugin_command:
            if os.path.exists(self.path_converter(f'{self.__plugin_dir}{control_plugin}/db/{str(chat_id)}.db')):
                with open(self.path_converter(f'{self.__plugin_dir}{control_plugin}/db/{str(chat_id)}.db'), "r") as f:
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

    def __logging_for_pluginRun(self, message, plugin, update_id):
        title = ""  # INFO Log
        user_name = ""
        from_id = ""

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
        elif "from" in message.keys():
            from_id = message["from"]["id"]
            if "first_name" in message["from"].keys():
                user_name += message["from"]["first_name"]
            if "last_name" in message["from"].keys():
                if "first_name" in message["from"].keys():
                    user_name += " " + message["from"]["last_name"]
                else:
                    user_name += message["from"]["last_name"]

        if message["message_type"] == "unknown":
            if not self.__hide_info:
                _logger.info(
                    f"[{update_id}]" + \
                    "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
                    "User:" + user_name + "(" + str(from_id) + ") - " + \
                    "Plugin:" + "" + " - " + \
                    "Type:" + message["message_type"])
        else:
            if not self.__hide_info:
                _logger.info(
                    f"[{update_id}] " + \
                    "From:" + title + "(" + str(message["chat"]["id"]) + ") - " + \
                    "User:" + user_name + "(" + str(from_id) + ") - " + \
                    "Plugin:" + str(plugin) + " - " + \
                    "Type:" + message["message_type"])

    def __make_token(self, len=64):
        """
        Generate a token of the specified length
        """
        if len > 64:
            return "Specified length is too long."
        else:
            token = ''.join(random.sample(f'{string.ascii_letters}{string.digits}-_', len))
            return token

    def _pluginRun(self, bot, message):
        """
        Run plugin
        """
        if message is None:
            return

        try:
            now_plugin_bridge, now_non_plugin_list = _bridge(self.__plugin_dir)
            now_plugin_info = _plugin_info(now_plugin_bridge.keys(), self.__plugin_dir)
            now_non_plugin_info = _plugin_info(now_non_plugin_list, self.__plugin_dir)

            if now_plugin_bridge != self.__plugin_bridge: # Dynamic Loading Plugin
                self.__load_plugin(now_plugin_info=now_plugin_info, now_plugin_bridge=now_plugin_bridge)
            if len(now_plugin_info) != len(self.__plugin_info) or \
                now_plugin_info != self.__plugin_info: # Dynamically update plugin information
                for plugin_name in list(self.__plugin_bridge.keys()):
                    self.__update_plugin(plugin_name) # Hot Update Plugin

            if now_non_plugin_list != self.__non_plugin_list: # Dynamically loading non-plugin packages
                self.__load_plugin(now_plugin_info=now_non_plugin_info, as_plugin=False,
                    now_non_plugin_list=now_non_plugin_list)
            if len(now_non_plugin_info) != len(self.__non_plugin_info) or \
                now_non_plugin_info != self.__non_plugin_info: # Dynamic update  the information of non-plugin package
                for plugin_name in list(self.__non_plugin_list):
                    self.__update_plugin(plugin_name, as_plugin=False) # Hot update non-plugin package

            if len(self.__plugin_bridge) == 0:
                os.system("")
                _logger.warn("\033[1;31mNo plugins installed\033[0m")

            self._update_plugins_init_status() # Update plugins init status
            self._plugins_init(bot)

            ok, buffer_status = self.buffer.status() # Buffer capacity monitoring
            if ok and buffer_status["used"] >= buffer_status["size"]:
                os.system("")
                _logger.warn("\033[1;31mThe data buffer area is full \033[0m")

            plugin_bridge = self.__control_plugin( # pluginctl control
                self.__plugin_bridge, message["chat"]["type"], message["chat"]["id"])

            message_type = ""
            message_type, message = self.__mark_message_for_pluginRun(message) # Category tagging messages

            if message_type == "unknown":
                self.__logging_for_pluginRun(message, "unknown", message["update_id"])
                return

        except Exception as e:
            _logger.error(f"[{message['update_id']}] Run plugin error: {e}")
            traceback.print_exc()
            return

        for plugin, command in plugin_bridge.items():
            try:
                if message_type == "query":
                    if command in ["", " ", None]:
                        continue

                if message.get(message_type)[:len(command)] == command:
                    plugin_requires_version = ""
                    ok, data = self.metadata.read(plugin_name=plugin)
                    if ok:
                        plugin_requires_version = data.get("Requires-teelebot", {})
                        plugin_requires_version = plugin_requires_version.replace(">", "").replace("<", "").replace("=", "")
                        if plugin_requires_version in [None, "", " "]:
                            _logger.warn(f"[{message['update_id']}] Skip run {plugin} plugin: failed to get the version of the plugin")
                            continue
                    else:
                        _logger.warn(f"[{message['update_id']}] Skip run {plugin} plugin: failed to get information about the plugin (error: {data})")
                        continue
                    if plugin_requires_version > self.version:
                        _logger.warn(f"[{message['update_id']}] Skip run {plugin} plugin: the plugin requires teelebot version >= {plugin_requires_version}")
                        continue

                    no_plugin_path = f'{self.__plugin_dir}{plugin}.py'
                    if os.path.exists(no_plugin_path):
                        _logger.warn(f"[{message['update_id']}] Skip run {plugin} plugin: there is a module named '{plugin}.py' under the plugin dir with the same name as plugin {plugin} ({no_plugin_path})")
                        continue

                    if self.__thread_pool._work_queue.qsize() >= self.__thread_pool._max_workers:
                        if not self.__hide_info:
                            _logger.info(f"[{message['update_id']}] Delay run {plugin} plugin: until a thread pool slot is available.")

                    def pluginFuncWrap(bot, message, plugin):
                        module = self.__import_module(plugin)
                        pluginFunc = getattr(module, plugin)
                        self.__logging_for_pluginRun(message, plugin, message["update_id"])
                        pluginFunc(bot, message)
                    fur = self.__thread_pool.submit(pluginFuncWrap, bot, message, plugin)
                    fur.add_done_callback(self.__threadpool_exception)
            
                    self.__response_times += 1

                    if message["chat"]["type"] != "private" and \
                    message["chat"]["id"] not in self.__response_chats:
                        self.__response_chats.append(message["chat"]["id"])
                    if message["from"]["id"] not in self.__response_users:
                        if not message["from"]["is_bot"]:
                            self.__response_users.append(message["from"]["id"])

            except Exception as e:
                _logger.error(f"[{message['update_id']}] Run {plugin} plugin error: {e}")
                traceback.print_exc()

    def _washUpdates(self, results):
        """
        Cleaning the message queue,
        The results should be a list
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
            update_ids.append(result.get("update_id"))
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

            if query_or_message == "inline_query":
                inline_query = result.get(query_or_message)
                inline_query["update_id"] = result["update_id"]
                inline_query["message_id"] = result["update_id"]
                inline_query["chat"] = inline_query.get("from")
                inline_query["chat"].pop("language_code")
                inline_query["chat"].pop("is_bot")
                inline_query["chat"]["type"] = "private"
                inline_query["text"] = ""
                inline_query["query"] = f'{self.__inline_mode_prefix}{inline_query["query"]}' # Inline Mode Plugin Prefix
                messages.append(inline_query)
            elif query_or_message == "callback_query":
                callback_query = result.get(query_or_message).get("message")
                callback_query["update_id"] = result["update_id"]
                callback_query["click_user"] = result.get(query_or_message)[
                    "from"]
                callback_query["callback_query_id"] = result.get(
                    query_or_message).get("id")
                callback_query["callback_query_data"] = result.get(
                    query_or_message).get("data")
                messages.append(callback_query)
            elif query_or_message == "my_chat_member":
                my_chat_member = result.get(query_or_message)
                my_chat_member["update_id"] = result["update_id"]
                my_chat_member["message_id"] = result.get("update_id")
                my_chat_member["my_chat_member_id"] = result.get("update_id")
                messages.append(my_chat_member)
            elif query_or_message == "chat_member":
                chat_member = result.get(query_or_message)
                chat_member["update_id"] = result["update_id"]
                chat_member["message_id"] = result.get("update_id")
                chat_member["chat_member_id"] = result.get("update_id")
                messages.append(chat_member)
            elif query_or_message == "chat_join_request":
                chat_join_request = result.get(query_or_message)
                chat_join_request["update_id"] = result["update_id"]
                chat_join_request["message_id"] = result.get("update_id")
                chat_join_request["chat_join_request_id"] = result.get("update_id")
                messages.append(chat_join_request)
            else:
                message_dict = result.get(query_or_message)
                if isinstance(message_dict, dict):
                    message_dict["update_id"] = result["update_id"]
                messages.append(message_dict)

        if len(update_ids) >= 1:
            self._offset = max(update_ids) + 1
            return messages
        else:
            return None
    
    # teelebot method
    def message_deletor(self, time_gap: int, chat_id: str, message_id: str) -> str:
        """
        Timed deletion of a message, time range: [0, 900], in seconds
        """
        if time_gap < 0 or time_gap > 900:
            _logger.error(f"[{chat_id}:{message_id}][{time_gap}s] Message deletion error: parameter time_gap is out of range.")
            return "time_gap_error"
        else:
            def message_deletor_func(time_gap, chat_id, message_id):
                if not self.__hide_info:
                    _logger.info(f"[{chat_id}:{message_id}][{time_gap}s] Message deleting...")

                if time_gap > 0:
                    time.sleep(int(time_gap))
                ok = self.deleteMessage(chat_id=chat_id, message_id=message_id)
                
                if ok:
                    if not self.__hide_info:
                        _logger.info(f"[{chat_id}:{message_id}][{time_gap}s] Message deleted.")
                else:
                    _logger.error(f"[{chat_id}:{message_id}][{time_gap}s] Message deletion error.")

            if time_gap == 0:
                message_deletor_func(time_gap, chat_id, message_id)
            else:
                if self.__timer_thread_pool._work_queue.qsize() >= self.__timer_thread_pool._max_workers:
                    if not self.__hide_info:
                        _logger.info(f"[{chat_id}:{message_id}][{time_gap}s] Delay delete message: until a thread pool slot is available.")

                fur = self.__timer_thread_pool.submit(
                    message_deletor_func, time_gap, chat_id, message_id)
                fur.add_done_callback(self.__threadpool_exception)

            return "ok"

    def timer(self, time_gap: int, func: Callable[..., None], *args: tuple) -> str:
        """
        Single timer, time range: [0, 900], unit seconds
        """
        if time_gap < 0 or time_gap > 900:
            return "time_gap_error"
        else:
            def timer_func(time_gap, func, *args):
                if not self.__hide_info:
                    _logger.info(f"[{id(timer_func)}][{time_gap}s] Timer executing...")

                time.sleep(int(time_gap))
                try:
                    func(*args)

                    if not self.__hide_info:
                        _logger.info(f"[{id(timer_func)}][{time_gap}s] Timer executed.")
                except Exception as e:
                    _logger.error(f"[{id(timer_func)}][{time_gap}s] Timer execution error: {e}")
                    traceback.print_exc()

            if len(args) == 1 and isinstance(args[0], tuple):
                args = args[0]

            if time_gap == 0:
                if not self.__hide_info:
                    _logger.info(f"[{id(timer_func)}][{time_gap}s] Timer executing...")
                try:
                    func(*args)

                    if not self.__hide_info:
                        _logger.info(f"[{id(timer_func)}][{time_gap}s] Timer executed.")
                except Exception as e:
                    _logger.error(f"[{id(timer_func)}][{time_gap}s] Timer execution error: {e}")
                    traceback.print_exc()
            else:
                if self.__timer_thread_pool._work_queue.qsize() >= self.__timer_thread_pool._max_workers:
                    if not self.__hide_info:
                        _logger.info(f"[{id(timer_func)}][{time_gap}s] Delay execution timer: until a thread pool slot is available.")

                fur = self.__timer_thread_pool.submit(
                    timer_func, time_gap, func, *args)
                fur.add_done_callback(self.__threadpool_exception)

            return "ok"

    def path_converter(self, path: str) -> str:
        """
        Convert URI according to operating system
        """

        path = str(Path(path))

        return path
    
    def join_plugin_path(self, path: str, plugin_name: str = None) -> str:
        """
        Automatically concatenate the provided path into the plugin directory URI
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]
        
        return self.path_converter(f"{self.plugin_dir}{plugin_name}{os.sep}{path}")
            
    def getChatCreator(self, chat_id: str) -> Union[bool, dict]:
        """
        Get group creator information
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
        Get group user status
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
        Generated file download link,
        Attention: The download link contains the Bot Key
        """
        req = self.getFile(file_id=file_id)
        if req:
            file_path = req["file_path"]
            if (self._local_api_server != "False" and
                "telegram.org" not in self._basic_url):
                return file_path
            else:
                file_download_path = f'{self._basic_url}file/bot{self._key}/{file_path}'
                return file_download_path
        else:
            return False

    def getChatAdminsUseridList(self, chat_id, skip_bot: bool = True,
                                privilege_users: list = None) -> Union[bool, list]:
        """
        Get the list of admin user_id in the chat
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
        Get plugin bridge
        """

        return copy.deepcopy(self.__plugin_bridge)

    @property
    def plugin_dir(self):
        """
        Get plugin dir
        """

        return self.__plugin_dir

    @property
    def version(self):
        """
        Get the teelebot version number
        """

        return self.__VERSION

    @property
    def author(self):
        """
        Author information
        """

        return self.__AUTHOR

    @property
    def root_id(self):
        """
        Get the user_id of bot admin
        """

        return self.__root_id

    @property
    def bot_id(self):
        """
        Get the user_id of bot
        """

        return self.__bot_id

    @property
    def uptime(self):
        """
        Get the running time of the framework (measured in seconds)
        """
        second = int(time.time()) - self.__start_time

        return second

    @property
    def response_times(self):
        """
        Get the total number of commands responded by the framework since startup
        """
        return self.__response_times

    @property
    def response_chats(self):
        """
        Get all the chat IDs that the framework has responded to since startup
        """
        return copy.deepcopy(self.__response_chats)

    @property
    def response_users(self):
        """
        Get all the user IDs that the framework has responded to since startup
        """
        return copy.deepcopy(self.__response_users)
    
    @property
    def proxies(self):
        """
        Get proxy information
        """
        return copy.deepcopy(self.__proxies)


class MethodPositionalArgumentError(Exception):
    def init(self, value):
        self.value = value
    def str(self):
        return f'MethodPositionalArgumentError: {self.value}'


