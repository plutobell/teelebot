# -*- coding:utf-8 -*-
'''
creation time: 2020-6-26
last_modify: 2020-11-10
'''
import os

def Uptime(bot, message):

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    prefix = "uptime"

    if not os.path.exists(bot.path_converter(bot.plugin_dir + "Uptime/config.ini")):
        detail_links = None
    else:
        with open(bot.path_converter(bot.plugin_dir + "Uptime/config.ini"), 'r') as f:
            detail_links = f.readline().strip()

    if text[1:len(prefix)+1] == prefix:
        time_format = bot.uptime(time_format="format")
        time_second = bot.uptime(time_format="second")
        response_times = bot.response_times()
        response_chats = len(bot.response_chats())
        response_users = len(bot.response_users())
        status = bot.sendChatAction(chat_id, "typing")
        inlineKeyboard = [
                    [
                        {"text": "详细信息", "url": detail_links}
                    ]
                ]
        if detail_links is not None:
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }
        else:
            reply_markup = None
        msg = "感谢您的关心 <b>(￣ε ￣)</b> %0A%0A我已经运行 <b>" +  str(time_second) + "</b> 秒%0A" +\
                "即：<b>" + str(time_format) + "</b>%0A%0A" +\
                "在此期间：%0A" +\
                "响应指令 <b>" + str(response_times) + "</b> 次%0A" +\
                "服务群组 <b>" + str(response_chats) + "</b> 个%0A" +\
                "服务用户 <b>" + str(response_users) + "</b> 名%0A%0A"
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)
        bot.message_deletor(15, chat_id, status["message_id"])