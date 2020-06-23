# -*- coding:utf-8 -*-
import requests
import time

def Bing(bot, message):
    prefix = "bing"
    text = message["text"]

    if text[1:len(prefix)+1] == prefix:
        img = bing_img()
        if img != False:
            img_url = img["url"]
            copyright_ = img["copyright"]
            startdate = img["startdate"]
            date = startdate[:4] + '-' + startdate[4:6] + '-' + startdate[6:]
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendPhoto(chat_id=message["chat"]["id"], photo=img_url, caption=copyright_+"%0A%0A"+date, parse_mode="HTML", reply_to_message_id=message["message_id"])
        else:
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="获取失败，请重试!", parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=message["chat"]["id"], text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(15, chat_id, status["message_id"])

def bing_img():
    url = "https://api.asilu.com/bg/"
    with requests.post(url=url, verify=False) as req:
        if not req.status_code == requests.codes.ok:
            return False
        elif req.json().get("images"):
            return req.json().get("images")[0]
        else:
            return False
