# -*- coding:utf-8 -*-
'''
description:基于Telegram Bot Api 的机器人
creation date: 2019-8-13
last modify: 2019-8-22
author github: plutobell
version: 1.1.2
'''

import requests, time, importlib, sys, threading
from .config import config

requests.adapters.DEFAULT_RETRIES = 5

class Bot(object):
    "机器人的基类"

    def __init__(self, key=""):
        if key != "":
            self.key = key
        elif key == "":
            self.key = config["key"]
        self.basic_url = "https://api.telegram.org/"
        self.url = self.basic_url + r"bot" + self.key + r"/"
        self.timeout = config["timeout"]
        self.offset = 0
        self.debug = config["debug"]
        self.plugin_dir = config["plugin_dir"]
        self.VERSION = config["version"]

    def __import_module(self, plugin_name):
        sys.path.append(self.plugin_dir + plugin_name + r"/")
        Module = importlib.import_module(plugin_name) #模块检测，待完善

        return Module

    def _run(self):
        print("机器人开始轮询", "version:" + self.VERSION)
        from .bridge import bridge
        plugin_list = []
        plugin_bridge = bridge()
        for key in plugin_bridge.keys():
            plugin_list.append(key)
        while(True):
            messages = self.getUpdates() #获取消息队列messages
            if messages == None:
                continue
            for message in messages: #获取单条消息记录message
                for plugin in plugin_list:
                    if message.get("text") != None:
                        message_type = "text"
                    elif message.get("caption") != None:
                        message_type = "caption"
                    else:
                        continue
                    if message.get(message_type)[:len(plugin)] == plugin:
                        Module = self.__import_module(plugin_bridge[plugin])
                        threadObj = threading.Thread(target=getattr(Module, plugin_bridge[plugin]), args=[message])
                        threadObj.start()
            time.sleep(0.2) #经测试，延时0.2s较为合理

    def getMe(self): #获取机器人基本信息
        command = "getMe"
        addr = command + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)
        return req.json()

    def getUpdates(self): #获取消息队列
        command = "getUpdates"
        addr = command + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        req = requests.get(self.url + addr)
        #req.keep_alive = False
        if self.debug is True:
            print(req.text)
        if req.json().get("ok") == True:
            update_ids = []
            messages = []
            results = req.json().get("result")
            for result in results:
                update_ids.append(result.get("update_id"))
                messages.append(result.get("message"))
            if len(update_ids) >= 1:
                self.offset = max(update_ids) + 1
                return messages
            else:
                return None
        elif req.json().get("ok") == False:
            return False

    def getFile(self, file_id): #获取文件id
        command = "getFile"
        addr = command + "?file_id=" + file_id
        req = requests.get(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)
        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def downloadFile(self, file_path, save_path): #下载文件
        if file_path[:7] == "http://" or file_path[:7] == "https:/":
            req = requests.get(file_path)
        else:
            url = self.basic_url + "file/bot" + self.key + r"/" + file_path
            req = requests.get(url)
        file_name = file_path.split('/')[len(file_path.split('/'))-1]
        with open(save_path + '/' + file_name, "wb") as f:
            f.write(req.content)
        if  req.status_code == requests.codes.ok:
            return True
        else:
            return False

    def sendMessage(self, chat_id, text, parse_mode="text"): #发送消息
        command = "sendMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&text=" + text
        if parse_mode in ("html","markdown"):
            addr += "&parse_mode=" + parse_mode
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)

        return req.json().get("ok")

    def sendPhoto(self, chat_id, photo, caption=None, parse_mode="text"): #发送图片
        command = "sendPhoto"
        if photo[:7] == "http://" or photo[:7] == "https:/":
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
            if caption != None:
                addr += "&caption=" + caption
            if parse_mode in ("markdown","html"):
                addr += "&parse_mode" + parse_mode

            req = requests.post(self.url + addr)
            req.keep_alive = False
        else:
            file_data = {"photo" : open(photo, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

            if caption != None:
                addr += "&caption=" + caption
            if parse_mode in ("markdown","html"):
                addr += "&parse_mode" + parse_mode

            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendDocument(self, chat_id, document, caption=None, parse_mode="text"): #发送文件
        command = "sendDocument"
        if document[:7] == "http://" or document[:7] == "https:/":
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
            if caption != None:
                addr += "&caption=" + caption
            if parse_mode in ("markdown","html"):
                addr += "&parse_mode" + parse_mode

            req = requests.post(self.url + addr)
            req.keep_alive = False
        else:
            file_data = {"document" : open(document, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

            if caption != None:
                addr += "&caption=" + caption
            if parse_mode in ("markdown","html"):
                addr += "&parse_mode" + parse_mode

            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def kickChatMember(self, uid, chat_id, until_date=0): #踢人
        command = "kickChatMember"
        if until_date == 0:
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid)
        else:
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid) + "&until_date=" + str(until_date)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def unbanChatMember(self, uid, chat_id): #解除踢人所带来的黑名单时间
        command = "unbanChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def leaveChat(self, chat_id): #退出群组
        command = "leaveChat"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def getChat(self, chat_id): #获取群组基本信息
        command = "getChat"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.get(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def getChatAdministrators(self, chat_id): #获取群组所有管理员信息
        command = "getChatAdministrators"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.get(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def getChatMembersCount(self, chat_id): #获取群组成员总数
        command = "getChatMembersCount"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.get(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def getChatMember(self, uid, chat_id): #获取群组特定用户信息
        command = "getChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid)
        req = requests.get(self.url + addr)

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
        req = requests.post(self.url + addr, data = json.dumps(permissions))

        return req.json().get("ok")

    def restrictChatMember(self, uid, chat_id, permissions, until_date=0):
        '''
        修改用户权限
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
        command = "restrictChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(uid) + \
            "&until_date=" + str(until_date)
        req = requests.post(self.url + addr, data = json.dumps(permissions))

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

        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def pinChatMessage(self, chat_id, message_id, disable_notification=False): #置顶消息
        command = "pinChatMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id) + \
            "&disable_notification=" + str(disable_notification)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def unpinChatMessage(self,chat_id): #取消置顶消息
        command = "unpinChatMessage"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.post(self.url + addr)

        return req.json().get("ok")
