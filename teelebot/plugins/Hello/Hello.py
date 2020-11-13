# -*- coding:utf-8 -*-

def Hello(bot, message):
    #print("你好,世界!")
    bot.sendChatAction(message["chat"]["id"], "typing")
    bot.sendPhoto(message["chat"]["id"], bot.path_converter(bot.plugin_dir + "Hello/helloworld.png"), reply_to_message_id=message["message_id"])