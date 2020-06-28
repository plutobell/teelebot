# -*- coding:utf-8 -*-
'''
@description:基于Telegram Bot Api 的机器人
@creation date: 2019-8-13
@last modify: 2020-6-29
@author github:plutobell
@version: 1.8.8_dev
'''
import time
import sys
import os
import json
import shutil
import importlib
import threading
import requests

from .handler import config, bridge
from datetime import timedelta
from traceback import extract_stack
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Bot(object):
    "机器人的基类"

    def __init__(self, key=""):
        self.config = config()

        if key != "":
            self.key = key
            self.config["key"] = key
        elif key == "":
            self.key = self.config["key"]
        self.basic_url = "https://api.telegram.org/"
        self.url = self.basic_url + r"bot" + self.key + r"/"
        self.webhook = self.config["webhook"]
        self.timeout = self.config["timeout"]
        self.offset = 0
        self.debug = self.config["debug"]

        self.plugin_dir = self.config["plugin_dir"]
        self.plugin_bridge = self.config["plugin_bridge"]


        self.VERSION = self.config["version"]
        self.AUTHOR = self.config["author"]

        self.__start_time = int(time.time())
        self.__response_times = 0
        self.__thread_pool = ThreadPoolExecutor(max_workers=int(self.config["pool_size"]))
        self.__session = self.__connection_session(pool_connections=int(self.config["pool_size"]), pool_maxsize=int(self.config["pool_size"])*2)
        self.__plugin_info = self.config["plugin_info"]

        del self.config["plugin_info"]

    def __del__(self):
        self.__thread_pool.shutdown(wait=True)
        self.__session.close()
    #teelebot method
    def __connection_session(self, pool_connections=10, pool_maxsize=10, max_retries=5):
        session = requests.Session()
        session.verify = False

        adapter = requests.adapters.HTTPAdapter(pool_connections = pool_connections,
                pool_maxsize = pool_maxsize, max_retries = max_retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def __threadpool_exception(self, fur):
        now_time = time.strftime("%Y/%m/%d %H:%M:%S")
        if self.debug == True:
            print("\n\n" + "_" * 19 + " " + str(now_time) + " " + "_" * 19 + "\n")
            #print(fur.result())
        elif fur.exception() != None:
            print("\n\n" + "_" * 19 + " " + str(now_time) + " " + "_" * 19 + "\n")
            print(fur.result())

    def __import_module(self, plugin_name):
        sys.path.append(self.plugin_dir + plugin_name + r"/")
        Module = importlib.import_module(plugin_name) #模块检测

        now_mtime = mtime = os.stat(self.plugin_dir + plugin_name + "/" + plugin_name + ".py").st_mtime
        if now_mtime != self.__plugin_info[plugin_name]: #插件热更新
            if os.path.exists(self.plugin_dir + plugin_name + r"/__pycache__"):
                shutil.rmtree(self.plugin_dir + plugin_name + r"/__pycache__")
            self.__plugin_info[plugin_name] = now_mtime
            importlib.reload(Module)

        return Module

    def __debug_info(self, result):
        if self.debug == True and result.get("ok") == False:
            os.system("") #"玄学"解决Windows下颜色显示失效的问题...
            stack_info = extract_stack()
            if len(stack_info) == 8: #插件内
                print("\033[1;31;40mRequest failed!")
                print(len(stack_info))
                print(" From : " + stack_info[-3][2])
                print(" Path : " + stack_info[5][0])
                print(" Line : " + str(stack_info[5][1]))
                print("Method: " + stack_info[6][2])
                print("Result: " + str(result))
                print("\033[0m")
            elif len(stack_info) == 3: #外部调用
                print("\033[1;31;40mRequest failed!")
                print(" From : " + stack_info[0][0])
                print(" Path : " + stack_info[1][0])
                print(" Line : " + str(stack_info[0][1]))
                print("Method: " + stack_info[1][2])
                print("Result: " + str(result))
                print("\033[0m")

    def _pluginRun(self, bot, message):
        if message == None:
            return
        # if self.debug == True:
        #     print(message)

        now_plugin_bridge = bridge(self.plugin_dir) #动态装载插件
        if now_plugin_bridge != self.plugin_bridge:
            self.plugin_bridge = now_plugin_bridge

        plugin_list = self.plugin_bridge.keys()
        plugin_bridge = self.plugin_bridge

        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        if chat_type != "private" and "/pluginctl" in plugin_bridge.keys() and plugin_bridge["/pluginctl"] == "PluginCTL":
            if os.path.exists(self.plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"):
                with open(self.plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db", "r") as f:
                    plugin_setting = f.read().strip()
                plugin_list_off = plugin_setting.split(',')
                plugin_bridge_temp = {}
                for plugin in plugin_list:
                    plugin_temp = plugin
                    if plugin == "" or plugin == " ":
                        plugin = "nil"
                    if plugin not in plugin_list_off:
                        plugin = plugin_temp
                        plugin_bridge_temp[plugin] = plugin_bridge[plugin]
                plugin_bridge = plugin_bridge_temp
                plugin_list = plugin_bridge.keys()

        for plugin in plugin_list:
            if "callback_query_id" in message.keys(): #callback query
                message_type = "callback_query_data"
            elif ("new_chat_members" in message.keys()) or ("left_chat_member" in message.keys()):
                message_type = "text"
                message["text"] = "" #default prefix of command
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
                message_type = "text"
            elif "caption" in message.keys():
                message_type = "caption"
            elif "query" in message.keys():
                message_type = "query"
            else:
                continue

            if message.get(message_type)[:len(plugin)] == plugin:
                Module = self.__import_module(plugin_bridge[plugin])
                pluginFunc = getattr(Module, plugin_bridge[plugin])
                fur = self.__thread_pool.submit(pluginFunc, bot, message)
                fur.add_done_callback(self.__threadpool_exception)

                self.__response_times += 1

    def _washUpdates(self, results):
        '''
        清洗消息队列
        results应当是一个列表
        '''
        if results == False or len(results) < 1:
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
                callback_query["click_user"] = result.get(query_or_message)["from"]
                callback_query["callback_query_id"] = result.get(query_or_message).get("id")
                callback_query["callback_query_data"] = result.get(query_or_message).get("data")
                messages.append(callback_query)
            else:
                messages.append(result.get(query_or_message))
        if len(update_ids) >= 1:
            self.offset = max(update_ids) + 1
            return messages
        elif req.json().get("ok") == False:
            return False
        else:
            return None

    def message_deletor(self, time_gap, chat_id, message_id):
        '''
        定时删除一条消息，时间范围：[0, 900],单位秒
        '''
        if time_gap < 0 or time_gap > 900:
            return "time_error"
        else:
            def message_deletor_func(chat_id, message_id):
                self.deleteMessage(chat_id=chat_id, message_id=message_id)
            if time_gap == 0:
                message_deletor_func(chat_id, message_id)
            else:
                timer = threading.Timer(time_gap, message_deletor_func, args=[chat_id, message_id])
                timer.start()
            return "ok"

    def uptime(self, time_format="second"):
        '''
        获取框架的持续运行时间
        '''
        second = int(time.time()) - self.__start_time
        if time_format == "second":
            return second
        elif time_format == "format":
            format_time = timedelta(seconds=second)
            return format_time
        else:
            return False

    def response_times(self):
        '''
        获取框架启动后响应指令的统计次数
        '''

        return self.__response_times

    #Getting updates
    def getUpdates(self, limit=100, allowed_updates=None):
        '''
        获取消息队列
        '''
        command = "getUpdates"
        addr = command + "?offset=" + str(self.offset) +\
            "&limit=" + str(limit) + "&timeout=" + str(self.timeout)

        if allowed_updates != None:
            with self.__session.get(self.url + addr, json=allowed_updates) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.get(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def setWebhook(self, url, certificate=None, max_connections=None, allowed_updates=None):
        '''
        设置Webhook
        Ports currently supported for Webhooks: 443, 80, 88, 8443.
        '''
        command = "setWebhook"
        addr = command + "?url=" + str(url)
        if max_connections != None:
            addr += "&max_connections=" + str(max_connections)
        if allowed_updates != None:
            addr += "&allowed_updates=" + str(allowed_updates)

        file_data = None
        if certificate != None:
            if type(certificate) == bytes:
                file_data = {"certificate" : certificate}
            else:
                file_data = {"certificate" : open(certificate, 'rb')}

        if file_data == None:
            req = self.__session.post(self.url + addr)
        else:
            req = self.__session.post(self.url + addr, files=file_data)

        self.__debug_info(req.json())
        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json()

    def deleteWebhook(self):
        '''
        删除设置的Webhook
        '''
        command = "deleteWebhook"
        addr = command
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getWebhookInfo(self):
        '''
        获取当前的Webhook状态
        '''
        command = "getWebhookInfo"
        addr = command
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")


    #Available methods
    def getMe(self): #获取机器人基本信息
        command = "getMe"
        addr = command + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getFile(self, file_id):
        '''
        获取文件信息
        '''
        command = "getFile"
        addr = command + "?file_id=" + file_id
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getFileDownloadPath(self, file_id):
        '''
        生成文件下载链接
        注意：下载链接包含Bot Key
        '''
        req = self.getFile(file_id=file_id)
        if req != False:

            file_path = req["file_path"]
            file_download_path = self.basic_url + "file/bot" + self.key + r"/" + file_path

            return file_download_path
        else:
            return False

    def sendMessage(self, chat_id, text, parse_mode="Text", reply_to_message_id=None, reply_markup=None): #发送消息
        command = "sendMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&text=" + text
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendVoice(self, chat_id, voice, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None): #发送音频消息 .ogg
        command = "sendVoice"
        if voice[:7] == "http://" or voice[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&voice=" + voice
        elif type(voice) == bytes:
            file_data = {"voice" : voice}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(voice) == str and '.' not in voice:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&voice=" + voice
        else:
            file_data = {"voice" : open(voice, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendAnimation(self, chat_id, animation, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None):
        '''
        发送动画 gif/mp4
        '''
        command = "sendAnimation"
        if animation[:7] == "http://" or animation[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&animation=" + animation
        elif type(animation) == bytes:
            file_data = {"animation" : animation}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(animation) == str and '.' not in animation:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&animation=" + animation
        else:
            file_data = {"animation" : open(animation, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendAudio(self, chat_id, audio, caption=None, parse_mode="Text", title=None, reply_to_message_id=None, reply_markup=None):
        '''
        发送音频 mp3
        '''
        command = "sendAudio"
        if audio[:7] == "http://" or audio[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&audio=" + audio
        elif type(audio) == bytes:
            file_data = {"audio" : audio}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(audio) == str and '.' not in audio:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&audio=" + audio
        else:
            file_data = {"audio" : open(audio, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode
        if title != None:
            addr += "&title=" + title
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendPhoto(self, chat_id, photo, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None): #发送图片
        '''
        发送图片
        '''
        command = "sendPhoto"
        if photo[:7] == "http://" or photo[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
        elif type(photo) == bytes:
            file_data = {"photo" : photo}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(photo) == str and '.' not in photo:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
        else:
            file_data = {"photo" : open(photo, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendVideo(self, chat_id, video, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None):
        '''
        发送视频
        '''
        command = "sendVideo"
        if video[:7] == "http://" or video[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video=" + video
        elif type(video) == bytes:
            file_data = {"video" : video}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(video) == str and '.' not in video:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video=" + video
        else:
            file_data = {"video" : open(video, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendVideoNote(self, chat_id, video_note, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None):
        '''
        发送圆形或方形视频？
        '''
        command = "sendVideoNote"
        if video_note[:7] == "http://" or video_note[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video_note=" + video_note
        elif type(video_note) == bytes:
            file_data = {"video_note" : video_note}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(video_note) == str and '.' not in video_note:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video_note=" + video_note
        else:
            file_data = {"video_note" : open(video_note, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id != None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:
                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def sendMediaGroup(self, chat_id, medias, disable_notification=None, reply_to_message_id=None, reply_markup=None): #暂未弄懂格式。
        '''
        以类似图集的方式发送图片或者视频(目前只支持http链接和文件id，暂不支持上传文件)
        media的格式：（同时请求需要加入header头，指定传送参数为json类型，并且将data由字典转为json字符串传送）
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
        '''
        command = "sendMediaGroup"
        addr = command + "?chat_id=" + str(chat_id)
        if disable_notification is not None:
            addr += "&disable_notification=" + str(disable_notification)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        headers = {'Content-Type': 'application/json'}
        with self.__session.post(self.url + addr, headers=headers, data=json.dumps(medias)) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendDocument(self, chat_id, document, caption=None, parse_mode="Text", reply_to_message_id=None, reply_markup=None): #发送文件
        command = "sendDocument"
        if document[:7] == "http://" or document[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
        elif type(document) == bytes:
            file_data = {"document" : document}
            addr = command + "?chat_id=" + str(chat_id)
        elif type(document) == str and '.' not in document:
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
        else:
            file_data = {"document" : open(document, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        if file_data == None:
            with self.__session.post(self.url + addr) as req:

                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")
        else:
            with self.__session.post(self.url + addr, files=file_data) as req:

                self.__debug_info(req.json())
                if req.json().get("ok") == True:
                    return req.json().get("result")
                elif req.json().get("ok") == False:
                    return req.json().get("ok")

    def leaveChat(self, chat_id): #退出群组
        command = "leaveChat"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getChat(self, chat_id):
        '''
        获取群组基本信息
        '''
        command = "getChat"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getChatAdministrators(self, chat_id):
        '''
        获取群组所有管理员信息
        '''
        command = "getChatAdministrators"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getChatMembersCount(self, chat_id):
        '''
        获取群组成员总数
        '''
        command = "getChatMembersCount"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        '''
        获取用户头像
        '''
        command = "getUserProfilePhotos"
        addr = command + "?user_id=" + str(user_id)

        if offset != None:
            addr += "&offset=" + str(offset)
        if limit != None and limit in list(range(1,101)):
            addr += "&limit=" + str(limit)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def getChatMember(self, uid, chat_id):
        '''
        获取群组特定用户信息
        '''
        command = "getChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatTitle(self, chat_id, title):
        '''
        设置群组标题
        '''
        command = "setChatTitle"
        addr = command + "?chat_id=" + str(chat_id) + "&title=" + str(title)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatDescription(self, chat_id, description):
        '''
        设置群组简介（测试好像无效。。）
        '''
        command = "setChatDescription"
        addr = command + "?chat_id=" + str(chat_id) + "&description=" + str(description)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatPhoto(self, chat_id, photo):
        '''
        设置群组头像
        '''
        command = "setChatPhoto"
        file_data = {"photo" : open(photo, 'rb')}
        addr = command + "?chat_id=" + str(chat_id)

        with self.__session.post(self.url + addr, files=file_data) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def deleteChatPhoto(self, chat_id):
        '''
        删除群组头像
        '''
        command = "deleteChatPhoto"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatPermissions(self, chat_id, permissions):
        '''
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
        '''
        import json
        command = "setChatPermissions"
        addr = command + "?chat_id=" +str(chat_id)
        with self.__session.post(self.url + addr, data = json.dumps(permissions)) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def restrictChatMember(self, chat_id, user_id, permissions, until_date=None):
        '''
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
        '''
        command = "restrictChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)
        if len(permissions) != 8:
            return False
        if until_date is not None:
            until_date = int(time.time()) + int(until_date)
            addr += "&until_date=" + str(until_date)

        with self.__session.post(self.url + addr, json = permissions) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def promoteChatMember(self, uid, chat_id, can_change_info=None, can_post_messages=None, \
        can_edit_messages=None, can_delete_messages=None, can_invite_users=None, \
        can_restrict_members=None, can_pin_messages=None, can_promote_members=None):
        '''
        修改管理员权限(只能修改由机器人任命的管理员的权限,范围为机器人权限的子集)
        {
        'can_change_info':False,
        'can_post_messages':False,
        'can_edit_messages':False,
        'can_delete_messages':False,
        'can_invite_users':False,
        'can_restrict_members':False,
        'can_pin_messages':False,
        'can_promote_members':False
        }
        '''
        command = "promoteChatMember"

        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid)
        if can_change_info != None:
            addr += "&can_change_info=" + str(can_change_info)
        if can_post_messages != None:
            addr += "&can_post_messages=" + str(can_post_messages)
        if can_edit_messages != None:
            addr += "&can_edit_messages=" + str(can_edit_messages)
        if can_delete_messages != None:
            addr += "&can_delete_messages=" + str(can_delete_messages)
        if can_invite_users != None:
            addr += "&can_invite_users=" + str(can_invite_users)
        if can_restrict_members != None:
            addr += "&can_restrict_members=" + str(can_restrict_members)
        if can_pin_messages != None:
            addr += "&can_pin_messages=" + str(can_pin_messages)
        if can_promote_members != None:
            addr += "&can_promote_members=" + str(can_promote_members)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def pinChatMessage(self, chat_id, message_id, disable_notification=None):
        '''
        置顶消息
        '''
        command = "pinChatMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)
        if disable_notification != None:
            addr += "&disable_notification=" + str(disable_notification)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def unpinChatMessage(self,chat_id):
        '''
        取消置顶消息
        '''
        command = "unpinChatMessage"
        addr = command + "?chat_id=" + str(chat_id)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None): #发送地图定位，经纬度
        command = "sendLocation"
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(float(latitude)) + "&longitude=" + str(float(longitude))
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendContact(self, chat_id, phone_number, first_name, last_name=None, reply_to_message_id=None, reply_markup=None):
        '''
        发送联系人信息
        '''
        command = "sendContact"
        addr = command + "?chat_id=" + str(chat_id) + "&phone_number=" + str(phone_number) + "&first_name=" + str(first_name)
        if last_name != None:
            addr += "&last_name=" + str(last_name)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendVenue(self, chat_id, latitude, longitude, title, address, reply_to_message_id=None, reply_markup=None):
        '''
        发送地点，显示在地图上
        '''
        command = "sendVenue"
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(float(latitude)) + "&longitude=" + str(float(longitude)) + \
            "&title=" + str(title) + "&address=" + str(address)
        if reply_to_message_id is not None:
            addr += "&reply_to_message_id=" + str(reply_to_message_id)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def sendChatAction(self, chat_id, action):
        '''
        发送聊天状态，类似： 正在输入...
            typing :for text messages,
            upload_photo :for photos,
            record_video/upload_video :for videos,
            record_audio/upload_audio :for audio files,
            upload_document :for general files,
            find_location :for location data,
            record_video_note/upload_video_note :for video notes.
        '''
        command = "sendChatAction"
        addr = command + "?chat_id=" + str(chat_id) + "&action=" + str(action)
        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        '''
        转发消息
        '''
        command = "forwardMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&from_chat_id=" + str(from_chat_id) \
            + "&message_id=" + str(message_id)
        if disable_notification != None:
            addr += "&disable_notification=" + str(disable_notification)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def kickChatMember(self, chat_id, user_id, until_date=None):
        '''
        从Group、Supergroup或者Channel中踢人，被踢者在until_date期限内不可再次加入
        until_date format:
        timestamp + offset
        '''

        command = "kickChatMember"
        if until_date is not None:
            until_date = int(time.time()) + int(until_date)
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id) + "&until_date=" + str(until_date)
        if until_date is None:
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def unbanChatMember(self, chat_id, user_id):
        '''
        解除user被设置的until_date
        ChatPermissions:
        can_send_messages
        can_send_media_messages
        can_send_polls
        can_send_other_messages
        can_add_web_page_previews
        can_change_info
        can_invite_users
        can_pin_messages
        '''

        command = "unbanChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatAdministratorCustomTitle(self, chat_id, user_id, custom_title):
        '''
        为群组的管理员设置自定义头衔
        '''
        command = "setChatAdministratorCustomTitle"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id) + "&custom_title=" + str(custom_title)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatPermissions(self, chat_id, can_change_info, can_post_messages, \
                        can_edit_messages, can_delete_messages, can_invite_users, \
                        can_restrict_members, can_pin_messages, can_promote_members):
        '''
        设置群组全局用户默认权限
        ChatPermissions:
        can_send_messages
        can_send_media_messages
        can_send_polls
        can_send_other_messages
        can_add_web_page_previews
        can_change_info
        can_invite_users
        can_pin_messages
        '''

        command = "setChatPermissions"
        addr = command + "?chat_id=" + str(chat_id)
        addr += "&can_change_info=" + str(can_change_info)
        addr += "&can_post_messages=" + str(can_post_messages)
        addr += "&can_edit_messages=" + str(can_edit_messages)
        addr += "&can_delete_messages=" + str(can_delete_messages)
        addr += "&can_invite_users=" + str(can_invite_users)
        addr += "&can_restrict_members=" + str(can_restrict_members)
        addr += "&can_pin_messages=" + str(can_pin_messages)
        addr += "&can_promote_members=" + str(can_promote_members)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def exportChatInviteLink(self, chat_id):
        '''
        使用此方法生成新的群组分享链接，旧有分享链接全部失效,成功返回分享链接
        '''
        command = "exportChatInviteLink"
        addr = command + "?chat_id=" + str(chat_id)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def setChatStickerSet(self, chat_id, sticker_set_name):
        '''
        为一个超级群组设置贴纸集
        '''
        command = "setChatStickerSet"
        addr = command + "?chat_id=" + str(chat_id) + "&sticker_set_name=" + str(sticker_set_name)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def deleteChatStickerSet(self, chat_id):
        '''
        删除超级群组的贴纸集
        '''
        command = "deleteChatStickerSet"
        addr = command + "?chat_id=" + str(chat_id)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    #Updating messages
    def editMessageText(self, text, chat_id=None, message_id=None, inline_message_id=None, \
            parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        '''
        编辑一条文本消息.成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        '''
        command = "editMessageText"

        if inline_message_id == None:
            if message_id == None or chat_id == None:
                return False

        if inline_message_id != None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        addr += "&text=" + str(text)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + str(parse_mode)
        if disable_web_page_preview is not None:
            addr += "&disable_web_page_preview=" + str(disable_web_page_preview)
        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def editMessageCaption(self, chat_id=None, message_id=None, inline_message_id=None, caption=None, parse_mode=None, reply_markup=None):
        '''
        编辑消息的Caption。成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        '''
        command = "editMessageCaption"
        if inline_message_id == None:
            if message_id == None or chat_id == None:
                return False

        if inline_message_id != None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if caption is not None:
            addr += "&caption=" + str(caption)
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + str(parse_mode)
        if reply_markup is not None:
            addr += "&reply_markup=" + str(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def editMessageMedia(self, media, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        '''
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
        '''
        command = "editMessageMedia"
        if inline_message_id == None:
            if message_id == None or chat_id == None:
                return False

        if inline_message_id != None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr, json=media) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json()

    def editMessageReplyMarkup(self, chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
        '''
        编辑MessageReplyMarkup
        在未指定inline_message_id的时候chat_id和message_id为必须存在的参数
        '''
        command = "editMessageReplyMarkup"
        if inline_message_id == None:
            if message_id == None or chat_id == None:
                return False

        if inline_message_id != None:
            addr = command + "?inline_message_id=" + str(inline_message_id)
        else:
            addr = command + "?chat_id=" + str(chat_id)
            addr += "&message_id=" + str(message_id)

        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def stopPoll(self, chat_id, message_id, reply_markup=None):
        '''
        停止投票？并返回最终结果
        '''
        command = "stopPoll"
        addr = command + "?chat_id" + str(chat_id) + "&message_id=" + str(message_id)

        if reply_markup != None:
            addr += "&reply_markup=" + json.dumps(reply_markup)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")

    def deleteMessage(self, chat_id, message_id):
        '''
        删除一条消息，机器人必须具备恰当的权限
        '''
        command = "deleteMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")


    #Inline mode
    def answerInlineQuery(self, inline_query_id, results, cache_time=None, \
                is_personal=None, next_offset=None, switch_pm_text=None, switch_pm_parameter=None):
        '''
        使用此方法发送Inline mode的应答
        '''
        command = "answerInlineQuery"
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

        with self.__session.post(self.url + addr, json=results) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json()

    def answerCallbackQuery(self, callback_query_id, text=None, show_alert="false", url=None, cache_time=0):
        '''
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
        '''
        command = "answerCallbackQuery"
        addr = command + "?callback_query_id=" + str(callback_query_id)
        if text != None:
            addr += "&text=" + str(text)
        if show_alert == "true":
            addr += "&show_alert=" + str(bool(show_alert))
        if url != None:
            addr += "&url=" + str(url)
        if cache_time != 0:
            addr += "&cache_time=" + str(cache_time)

        with self.__session.post(self.url + addr) as req:

            self.__debug_info(req.json())
            if req.json().get("ok") == True:
                return req.json().get("result")
            elif req.json().get("ok") == False:
                return req.json().get("ok")