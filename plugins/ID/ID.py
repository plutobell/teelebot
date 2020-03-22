# -*- coding:utf-8 -*-
from teelebot import Bot
from teelebot.handler import config

config = config()

def ID(message):
    bot = Bot()
    status = bot.sendChatAction(message["chat"]["id"], "typing")
    if str(message["from"]["id"]) == config["root"]:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        bot.sendMessage(message["chat"]["id"], "主人，" + "您的用户ID为：<b>" + str(message["from"]["id"]) + "</b>", "HTML")
    else:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        bot.sendMessage(message["chat"]["id"], str(message["from"]["first_name"]) + "%0A您的用户ID为：<b>" + str(message["from"]["id"]) + "</b>", "HTML")