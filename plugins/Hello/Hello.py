# -*- coding:utf-8 -*-

def Hello(bot, message):
    #print("你好,世界!")
    status = bot.sendChatAction(message["chat"]["id"], "typing")
    status = bot.sendPhoto(message["chat"]["id"], bot.plugin_dir + "Hello/helloworld.png", reply_to_message_id=message["message_id"])