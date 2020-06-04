# -*- coding:utf-8 -*-
'''
creation time: 2020-6-4
last_modify: 2020-6-4
'''

from teelebot import Bot
from teelebot.handler import config
from threading import Timer

config = config()
bot = Bot()
gap = 15

def Admin(message):
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message["text"]
    bot_id = str(bot.getMe()["id"])
    prefix = "admin"

    commad = {
            "/adminkick": "kick",
            "/admindel": "del"
        }
    count = 0
    for c in commad.keys():
        if c in str(text):
            count += 1

    if message["chat"]["type"] != "private":
        admins = administrators(chat_id=chat_id)
        admins.append(bot_id)
        if str(config["root"]) not in admins:
            admins.append(str(config["root"])) #root permission

    if message["chat"]["type"] == "private": #判断是否为私人对话
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话!", parse_mode="text", reply_to_message_id=message_id)
            timer = Timer(gap, timer_func_for_del, args=[chat_id, message_id])
            timer.start()
    elif text[1:len(prefix)+1] == prefix and count == 0: #菜单
        status = bot.sendChatAction(chat_id, "typing")
        msg = "<b>===== Admin 插件功能 =====</b>%0A%0A" +\
            "<b>/adminkick</b> - 踢人。格式:以回复要踢用户的消息的形式发送指令%0A" +\
            "<b>/admindel</b> - 删除一条消息。格式:以回复要删除的消息的形式发送指令%0A" +\
            "%0A..."
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])

        timer = Timer(30, timer_func_for_del, args=[chat_id, status["message_id"]])
        timer.start()

    elif "reply_to_message" in message.keys():
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(user_id) in admins and str(chat_id) == str(target_chat_id):
            if text[1:] == prefix + commad["/adminkick"]:
                if str(target_user_id) not in admins:
                    status = bot.kickChatMember(chat_id=chat_id, user_id=target_user_id, until_date=60)
                    status_ = bot.unbanChatMember(chat_id=chat_id, user_id=target_user_id)
                    if status != False:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text="已送该用户出群。", parse_mode="text", reply_to_message_id=message["message_id"])
                        timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                        timer.start()
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="抱歉，无权处置该用户!", parse_mode="text", reply_to_message_id=message["message_id"])
                    timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                    timer.start()
            elif text[1:] == prefix + commad["/admindel"]:
                status = bot.deleteMessage(chat_id=chat_id, message_id=target_message_id)

        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="抱歉，您无权操作!", parse_mode="text", reply_to_message_id=message["message_id"])

            timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
            timer.start()
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="未指定要操作的对象!", parse_mode="text", reply_to_message_id=message["message_id"])

        timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
        timer.start()

    timer = Timer(gap, timer_func_for_del, args=[chat_id, message_id])
    timer.start()


def administrators(chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
    else:
        admins = False

    return admins

def timer_func_for_del(chat_id, message_id):
    status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)