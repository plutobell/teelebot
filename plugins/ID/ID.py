# -*- coding:utf-8 -*-
from teelebot import Bot
from teelebot.handler import config\

config = config()

def ID(message):
    bot = Bot()
    status = bot.sendChatAction(message["chat"]["id"], "typing")
    if str(message["from"]["id"]) == config["root"]:
        bot.sendMessage(message["chat"]["id"], "尊敬的主人" + "%0A您的用户ID为：" + str(message["from"]["id"]), "html")
    else:
        bot.sendMessage(message["chat"]["id"], str(message["from"]["first_name"]) + "%0A您的用户ID为：" + str(message["from"]["id"]), "html")