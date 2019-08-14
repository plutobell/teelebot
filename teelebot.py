# -*-  encoding: utf-8  -*-
'''
description:基于Telegram Bot Api 的机器人
creation date: 2019-8-13
last modify: 2019-8-14
author github: plutobell
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
        self.url = r"https://api.telegram.org/bot" + self.key + r"/"
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
            froms, chats, dates, texts = self.getUpdates()
            for i,chat in enumerate(chats):
                if chat["id"] < 0:
                    print("(" + str(froms[i]["id"]) + ") " + froms[i]["first_name"] + ":", texts[i], dates[i], "( [" + str(chat["id"]) + "] - " + chat["title"] + ")")
                elif chat["id"] > 0:
                    print("(" + str(froms[i]["id"]) + ") " + froms[i]["first_name"] + ":", texts[i], dates[i])

                for plugin in plugin_list:
                    if texts[i][:len(plugin)] == plugin:
                        Module = self.__import_module(plugin_bridge[plugin])
                        threadObj = threading.Thread(target=getattr(Module, plugin_bridge[plugin]), args=[froms[i], chat, dates[i], texts[i]])
                        threadObj.start()
            time.sleep(0.2) #经测试，延时0.2s较为合理

    def __push(self, common, addr, file="None"):
        if common == "getMe": #获取机器人信息
            req = requests.post(self.url + addr)
            req.keep_alive = False
            if self.debug is True:
                print(req.text)

            return req.json().get("ok")

        elif common == "getUpdates": #接收
            req = requests.post(self.url + addr)
            req.keep_alive = False
            if self.debug is True:
                print(req.text)
            if req.json().get("ok") == True:
                update_ids = []
                froms = []
                chats = []
                dates = []
                texts = []
                results = req.json().get("result")
                for result in results:
                    update_ids.append(result.get("update_id"))
                    message = result.get("message")
                    chat = message.get("chat")
                    fromm = message.get("from")
                    if message.get("text") != None:
                        chats.append(chat)
                        froms.append(fromm)
                        dates.append(message.get("date"))
                        texts.append(message.get("text"))
                print(texts)

                if len(update_ids) >=1:
                    self.offset = max(update_ids) + 1
                return froms, chats,dates,texts
            elif req.json().get("ok") == False:
                return False, False, False, False

        elif common == "sendMessage":  #发送文本
            req = requests.post(self.url + addr)
            req.keep_alive = False
            if self.debug is True:
                print(req.text)

            return req.json().get("ok")

        elif common in ("sendPhoto","sendDocument") and file != "None": #发送文件
            f_type = ""
            if common == "sendPhoto": #发送图片
                f_type = "photo"
            elif common == "sendDocument": #发送其他文件
                f_type = "document"
            if file[:7] == "http://" or file[0:7] == "https:/":
                req = requests.post(self.url + addr + file)
                req.keep_alive = False
            else:
                uid = ""
                for i in range(len(addr[len(common)+9:])):
                    if addr[len(common)+9:][i] == '&':
                        break
                    uid += addr[len(common)+9:][i]
                file_data = {f_type : open(file, 'rb')}
                req = requests.post(self.url + common + "?chat_id=" + uid, files=file_data)

            return req.json().get("ok")


    def getMe(self):
        common = "getMe"
        addr = common + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        status = self.__push(common,addr)

        return status

    def getUpdates(self):
        common = "getUpdates"
        addr = common + "?" + "offset=" + str(self.offset) + "&timeout=" + str(self.timeout)
        status = self.__push(common, addr)

        return status

    def sendMessage(self, uid, text, model="text"):
        common = "sendMessage"
        if model in ("html","markdown"):
            addr = common + "?parse_mode=" + model + "&chat_id=" + str(uid) + "&text=" + text
        elif model == "text":
            addr = common + "?chat_id=" + str(uid) + "&text=" + text
        status = self.__push(common,addr)

        return status

    def sendPhoto(self, uid, photo):
        common = "sendPhoto"
        addr = common + "?chat_id=" + str(uid) + "&photo="
        status = self.__push(common, addr, photo)

        return status

    def sendDocument(self, uid, document):
        common = "sendDocument"
        addr = common + "?chat_id=" + str(uid) + "&document="
        status = self.__push(common, addr, document)

        return status

if __name__ == "__main__":
    bot = Bot()
    bot._run()