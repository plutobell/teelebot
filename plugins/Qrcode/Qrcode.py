# -*- coding:utf-8 -*-
from teelebot import Bot
from threading import Timer
import requests

bot = Bot()

def Qrcode(message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    gap= 30
    prefix = "qrcode"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="正在生成，请稍等...", parse_mode="HTML", reply_to_message_id=message_id)
            timer = Timer(5, timer_func, args=[chat_id, status["message_id"]])
            timer.start()

            img = qrcode_img(text.split(' ')[1])
            if img != False:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendPhoto(chat_id=chat_id, photo=img, caption="您的二维码已生成，消息将在不久后销毁，请尽快保存。", parse_mode="HTML", reply_to_message_id=message_id)
                timer = Timer(gap, timer_func, args=[chat_id, status["message_id"]])
                timer.start()
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="抱歉，生成失败，请重试。", parse_mode="HTML", reply_to_message_id=message_id)
                timer = Timer(15, timer_func, args=[chat_id, status["message_id"]])
                timer.start()
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            timer = Timer(15, timer_func, args=[chat_id, status["message_id"]])
            timer.start()
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        timer = Timer(15, timer_func, args=[chat_id, status["message_id"]])
        timer.start()



def qrcode_img(data):
    url_basic = "https://chart.apis.google.com/chart?cht=qr&chs=500x500&chl="
    url = url_basic + str(data)

    req = requests.post(url=url)
    if type(req.content) == bytes:
        return req.content
    else:
        return False

def timer_func(chat_id, message_id):
    status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)