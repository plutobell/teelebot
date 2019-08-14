# -*-  encoding: utf-8  -*-
import sys
sys.path.append("../")
from TeeleBot import teelebot

def Hello(fromm, chat, date, text):
    #print("你好,世界!")
    bot = teelebot.Bot()
    status = bot.sendPhoto(chat["id"], "plugins\\Hello\\helloworld.png")