# -*- coding:utf-8 -*-
'''
@description:基于Telegram Bot Api 的机器人
@creation date: 2019-8-13
@last modify: 2020-3-22
@author github: plutobell
@version: 1.2.3_dev
'''
import time
import sys
import json
import importlib
import threading

import requests
from .handler import config

config = config()
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
        self.debug = bool(config["debug"])
        self.plugin_dir = config["plugin_dir"]
        self.plugin_bridge = config["plugin_bridge"]
        self.VERSION = config["version"]

    def __import_module(self, plugin_name):
        sys.path.append(self.plugin_dir + plugin_name + r"/")
        Module = importlib.import_module(plugin_name) #模块检测，待完善

        return Module

    def _run(self):
        print("机器人开始轮询", "version:" + self.VERSION)
        plugin_list = []
        for key in self.plugin_bridge.keys():
            plugin_list.append(key)
        while(True):
            try:
                messages = self.getUpdates() #获取消息队列messages
                if messages == None or messages == False:
                    continue
                for message in messages: #获取单条消息记录message
                    for plugin in plugin_list:
                        if message == None:
                            continue
                        if message.get("text") != None:
                            message_type = "text"
                        elif message.get("caption") != None:
                            message_type = "caption"
                        elif message.get("query") != None:
                            message_type = "query"
                        else:
                            continue
                        if message.get(message_type)[:len(plugin)] == plugin:
                            Module = self.__import_module(self.plugin_bridge[plugin])
                            threadObj = threading.Thread(target=getattr(Module, self.plugin_bridge[plugin]), args=[message])
                            threadObj.start()
                time.sleep(0.2) #经测试，延时0.2s较为合理
            except KeyboardInterrupt: #判断键盘输入，终止循环
                print("程序终止") #退出存在问题，待修复
                sys.exit()

    #Getting updates
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
            if len(results) < 1:
                return None
            for result in results:
                query_or_message = ""
                if result.get("inline_query"):
                    query_or_message = "inline_query"
                elif result.get("message"):
                    query_or_message = "message"
                update_ids.append(result.get("update_id"))
                messages.append(result.get(query_or_message))
            if len(update_ids) >= 1:
                self.offset = max(update_ids) + 1
                return messages
            else:
                return None
        elif req.json().get("ok") == False:
            return False

    #Available methods
    def getMe(self): #获取机器人基本信息
        command = "getMe"
        addr = command + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)
        return req.json()

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

    def sendMessage(self, chat_id, text, parse_mode="Text"): #发送消息
        command = "sendMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&text=" + text
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode=" + parse_mode
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)

        return req.json().get("ok")

    def sendVoice(self, chat_id, voice, caption=None, parse_mode="Text"): #发送音频消息 .ogg
        command = "sendVoice"
        if voice[:7] == "http://" or voice[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&voice=" + voice
        else:
            file_data = {"voice" : open(voice, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendAnimation(self, chat_id, animation, caption=None, parse_mode="Text"):
        '''
        发送动画 gif/mp4
        '''
        command = "sendAnimation"
        if animation[:7] == "http://" or animation[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&animation=" + animation
        else:
            file_data = {"animation" : open(animation, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendAudio(self, chat_id, audio, caption=None, parse_mode="Text", title=None):
        '''
        发送音频 mp3
        '''
        command = "sendAudio"
        if audio[:7] == "http://" or audio[:7] == "https:/":
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

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendPhoto(self, chat_id, photo, caption=None, parse_mode="Text"): #发送图片
        command = "sendPhoto"
        if photo[:7] == "http://" or photo[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&photo=" + photo
        else:
            file_data = {"photo" : open(photo, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendVideo(self, chat_id, video, caption=None, parse_mode="Text"):
        '''
        发送视频
        '''
        command = "sendVideo"
        if video[:7] == "http://" or video[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video=" + video
        else:
            file_data = {"video" : open(video, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendVideoNote(self, chat_id, video_note, caption=None, parse_mode="Text"):
        '''
        发送圆形或方形视频？
        '''
        command = "sendVideoNote"
        if video_note[:7] == "http://" or video_note[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&video_note=" + video_note
        else:
            file_data = {"video_note" : open(video_note, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
            req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def sendMediaGroup(self, chat_id, medias, disable_notification=None, reply_to_message_id=None): #暂未弄懂格式。
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

        headers = {'Content-Type': 'application/json'}
        req = requests.post(self.url + addr, headers=headers, data=json.dumps(medias))

        return req.json().get("ok")

    def sendDocument(self, chat_id, document, caption=None, parse_mode="Text"): #发送文件
        command = "sendDocument"
        if document[:7] == "http://" or document[:7] == "https:/":
            file_data = None
            addr = command + "?chat_id=" + str(chat_id) + "&document=" + document
        else:
            file_data = {"document" : open(document, 'rb')}
            addr = command + "?chat_id=" + str(chat_id)

        if caption != None:
            addr += "&caption=" + caption
        if parse_mode in ("Markdown", "MarkdownV2", "HTML"):
            addr += "&parse_mode" + parse_mode

        if file_data == None:
            req = requests.post(self.url + addr)
        else:
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

    def getUserProfilePhotos(self, user_id, offset=None, limit=None): #获取用户头像
        command = "getUserProfilePhotos"
        addr = command + "?user_id=" + str(user_id)

        if offset != None:
            addr += "&offset=" + str(offset)
        if limit != None and limit in list(range(1,101)):
            addr += "&limit=" + str(limit)

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

    def setChatTitle(self, chat_id, title): #设置群组标题
        command = "setChatTitle"
        addr = command + "?chat_id=" + str(chat_id) + "&title=" + str(title)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def setChatDescription(self, chat_id, description): #设置群组简介（测试好像无效。。）
        command = "setChatDescription"
        addr = command + "?chat_id=" + str(chat_id) + "&description=" + str(description)
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def setChatPhoto(self, chat_id, photo): #设置群组头像
        command = "setChatPhoto"
        file_data = {"photo" : open(photo, 'rb')}
        addr = command + "?chat_id=" + str(chat_id)

        req = requests.post(self.url + addr, files=file_data)

        return req.json().get("ok")

    def deleteChatPhoto(self, chat_id): #删除群组头像
        command = "deleteChatPhoto"
        addr = command + "?chat_id=" + str(chat_id)
        req = requests.post(self.url + addr)

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

    def sendLocation(self, chat_id, latitude, longitude): #发送地图定位，经纬度
        command = "sendLocation"
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(float(latitude)) + "&longitude=" + str(float(longitude))
        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def sendContact(self, chat_id, phone_number, first_name, last_name=None):
        '''
        发送联系人信息
        '''
        command = "sendContact"
        addr = command + "?chat_id=" + str(chat_id) + "&phone_number=" + str(phone_number) + "&first_name=" + str(first_name)
        if last_name != None:
            addr += "&last_name=" + str(last_name)

        req = requests.post(self.url + addr)

        return req.json().get("ok")

    def sendVenue(self, chat_id, latitude, longitude, title, address):
        '''
        发送地点，显示在地图上
        '''
        command = "sendVenue"
        addr = command + "?chat_id=" + str(chat_id) + "&latitude=" + str(float(latitude)) + "&longitude=" + str(float(longitude)) + \
            "&title=" + str(title) + "&address=" + str(address)
        req = requests.post(self.url + addr)

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
        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def kickChatMember(self, chat_id, user_id, until_date=None):
        '''
        从Group、Supergroup或者Channel中踢人，被踢者在until_date期限内不可再次加入
        '''

        command = "kickChatMember"
        if until_date is not None:
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id) + "&until_date=" + str(until_date)
        if until_date is None:
            addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def restrictChatMember(self, chat_id, user_id, can_change_info, can_post_messages, \
                        can_edit_messages, can_delete_messages, can_invite_users, \
                        can_restrict_members, can_pin_messages, can_promote_members, until_date=None):
        '''
        限制群组用户权限
        '''
        command = "restrictChatMember"
        addr = command + "?chat_id=" + str(chat_id) + "&user_id=" + str(user_id)
        addr += "&can_change_info=" + str(can_change_info)
        addr += "&can_post_messages=" + str(can_post_messages)
        addr += "&can_edit_messages=" + str(can_edit_messages)
        addr += "&can_delete_messages=" + str(can_delete_messages)
        addr += "&can_invite_users=" + str(can_invite_users)
        addr += "&can_restrict_members=" + str(can_restrict_members)
        addr += "&can_pin_messages=" + str(can_pin_messages)
        addr += "&can_promote_members=" + str(can_promote_members)
        if until_date is not None:
            addr += "&until_date=" + str(until_date)

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

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

        req = requests.post(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def answerCallbackQuery(self, callback_query_id, text, show_alert, url, cache_time):
        pass


    #Updating messages
    def editMessageText(self, chat_id, text, message_id=None, inline_message_id=None, \
            parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        '''
        编辑一条文本消息.成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        '''
        command = "editMessageText"
        addr = command + "?chat_id=" + str(chat_id)
        if message_id is not None:
            addr += "&message_id=" + str(message_id)
        if inline_message_id is not None:
            addr += "&inline_message_id=" + str(inline_message_id)
        addr += "&text=" + str(text)
        if parse_mode in ("Markdown", "HTML"):
            addr += "&parse_mode=" + str(parse_mode)
        if disable_web_page_preview is not None:
            addr += "&disable_web_page_preview=" + str(disable_web_page_preview)
        if reply_markup is not None:
            addr += "&reply_markup=" + str(reply_markup)

        req = requests.post(self.url + addr)

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json()

    def editMessageCaption(self, chat_id, message_id, inline_message_id, text, parse_mode, reply_markup):
        '''
        编辑消息标题？成功时，若消息为Bot发送则返回编辑后的消息，其他返回True
        '''
        pass

    def editMessageMedia(self, chat_id, message_id, inline_message_id, media, reply_markup):
        pass

    def editMessageReplyMarkup(self, chat_id, message_id, inline_message_id, reply_markup):
        pass

    def stopPoll(self, chat_id, message_id, reply_markup):
        pass

    def deleteMessage(self, chat_id, message_id):
        '''
        删除一条消息，机器人必须具备恰当的权限
        '''
        command = "deleteMessage"
        addr = command + "?chat_id=" + str(chat_id) + "&message_id=" + str(message_id)

        req = requests.post(self.url + addr)

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

        headers = {'Content-Type':'application/json'}
        req = requests.post(self.url + addr, headers=headers, data=json.dumps(results))

        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json()