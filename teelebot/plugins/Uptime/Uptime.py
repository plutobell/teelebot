# -*- coding:utf-8 -*-
'''
creation time: 2020-6-26
last_modify: 2020-11-18
'''
import os
from datetime import timedelta

def Uptime(bot, message):

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    plugin_dir = bot.plugin_dir
    VERSION = bot.version
    prefix = "uptime"

    if not os.path.exists(bot.path_converter(plugin_dir + "Uptime/config.ini")):
        detail_links = None
    else:
        with open(bot.path_converter(plugin_dir + "Uptime/config.ini"), 'r') as f:
            detail_links = f.readline().strip()

    if text[1:len(prefix)+1] == prefix:
        time_second = bot.uptime
        time_format = timedelta(seconds=time_second)
        response_times = bot.response_times
        response_chats = len(bot.response_chats)
        response_users = len(bot.response_users)
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
        msg = "<code>感谢您的关心</code> <b>(￣ε ￣)</b> \n\n<code>我已经运行 <b>" +  str(time_second) + "</b> 秒\n" +\
                "即：<b>" + str(time_format) + "</b>\n\n" +\
                "在此期间：\n" +\
                "响应指令 <b>" + str(response_times) + "</b> 次\n" +\
                "服务群组 <b>" + str(response_chats) + "</b> 个\n" +\
                "服务用户 <b>" + str(response_users) + "</b> 名\n\n</code>" +\
                "<code>v" + str(VERSION) + "</code>"

        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)
        bot.message_deletor(15, chat_id, status["message_id"])