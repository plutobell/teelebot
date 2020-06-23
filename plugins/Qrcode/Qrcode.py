# -*- coding:utf-8 -*-
import requests

def Qrcode(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    gap= 30
    prefix = "qrcode"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            img = qrcode_img(text.split(' ')[1])
            if img != False:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendPhoto(chat_id=chat_id, photo=img, caption="您的二维码已生成，消息将在不久后销毁，请尽快保存。", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(gap, chat_id, status["message_id"])
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="抱歉，生成失败，请重试。", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])



def qrcode_img(data):
    url_basic = "https://chart.apis.google.com/chart?cht=qr&chs=500x500&chl="
    url = url_basic + str(data)

    with requests.post(url=url, verify=False) as req:
        if not req.status_code == requests.codes.ok:
            return False
        elif type(req.content) == bytes:
            return req.content
        else:
            return False
