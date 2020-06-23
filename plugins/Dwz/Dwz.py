# -*- coding:utf-8 -*-
import requests

def Dwz(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    gap= 30
    prefix = "dwz"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            if "https://" in text.split(' ')[1] or "http://" in text.split(' ')[1]:
                dwz_data = dwz(text.split(' ')[1])
                if dwz_data != False:
                    msg = "<b>短网址生成：</b>%0A" +\
                        "%0A原网址: " + str(dwz_data["long_url"]) +\
                        "%0A短网址: " + str(dwz_data["short_url"]) +\
                        "%0A%0A请保存短网址，本消息不久将被销毁"
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(30, chat_id, status["message_id"])
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="生成失败，请重试!", parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="网址需带上协议头，请重试!", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def dwz(url):
    url = "https://v1.alapi.cn/api/url?url=" + str(url)

    with requests.get(url=url, verify=False) as req:
        if not req.status_code == requests.codes.ok:
            return False
        elif req.json().get("code") == 200:
            return req.json().get("data")
        else:
            return False
