# -*- coding:utf-8 -*-
import sys
sys.path.append("../")
from TeeleBot import Bot

def Hello(message):
    #print("你好,世界!")
    bot = Bot()
    status = bot.sendPhoto(message["chat"]["id"], "plugins/Hello/helloworld.png")