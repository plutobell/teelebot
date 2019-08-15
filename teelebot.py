# -*-  encoding: utf-8  -*-
'''
description:基于Telegram Bot Api 的机器人
creation date: 2019-8-13
last modify: 2019-8-15
author github: plutobell
version: 1.0.7
'''

import requests, time, importlib, sys, threading
from config import config

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

    def __import_module(self, plugin_name):
        sys.path.append(r"plugins/" + plugin_name + r"/")
        Module = importlib.import_module(plugin_name) #模块检测，待完善

        return Module

    def _run(self):
        print("机器人开始轮询", "version:" + config["version"])
        from bridge import bridge
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
                    elif message.get("text") != None:
                        message_type = "caption"
                    else:
                        continue
                    if message.get(message_type)[:len(plugin)] == plugin:
                        Module = self.__import_module(plugin_bridge[plugin])
                        threadObj = threading.Thread(target=getattr(Module, plugin_bridge[plugin]), args=[message])
                        threadObj.start()
            time.sleep(0.2) #经测试，延时0.2s较为合理

    def getMe(self):
        common = "getMe"
        addr = common + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)
        return req.json()

    def getUpdates(self):
        common = "getUpdates"
        addr = common + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
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

    def getFile(self, file_id):
        common = "getFile"
        addr = common + "?file_id=" + file_id
        req = requests.get(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)
        if req.json().get("ok") == True:
            return req.json().get("result")
        elif req.json().get("ok") == False:
            return req.json().get("ok")

    def downloadFile(self, file_path, save_path):
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

    def sendMessage(self, uid, text, model="text"):
        common = "sendMessage"
        if model in ("html","markdown"):
            addr = common + "?parse_mode=" + model + "&chat_id=" + str(uid) + "&text=" + text
        elif model == "text":
            addr = common + "?chat_id=" + str(uid) + "&text=" + text
        req = requests.post(self.url + addr)
        req.keep_alive = False
        if self.debug is True:
            print(req.text)

        return req.json().get("ok")

    def sendPhoto(self, uid, photo):
        common = "sendPhoto"
        addr = common + "?chat_id=" + str(uid) + "&photo="
        if photo[:7] == "http://" or photo[:7] == "https:/":
                req = requests.post(self.url + addr + photo)
                req.keep_alive = False
        else:
            uid = ""
            for i in range(len(addr[len(common)+9:])):
                if addr[len(common)+9:][i] == '&':
                    break
                uid += addr[len(common)+9:][i]
            file_data = {"photo" : open(photo, 'rb')}
            req = requests.post(self.url + common + "?chat_id=" + uid, files=file_data)

        return req.json().get("ok")


    def sendDocument(self, uid, document):
        common = "sendDocument"
        addr = common + "?chat_id=" + str(uid) + "&document="
        if document[:7] == "http://" or document[:7] == "https:/":
                req = requests.post(self.url + addr + document)
                req.keep_alive = False
        else:
            uid = ""
            for i in range(len(addr[len(common)+9:])):
                if addr[len(common)+9:][i] == '&':
                    break
                uid += addr[len(common)+9:][i]
            file_data = {"document" : open(document, 'rb')}
            req = requests.post(self.url + common + "?chat_id=" + uid, files=file_data)

        return req.json().get("ok")


if __name__ == "__main__":
    bot = Bot()
    bot._run()