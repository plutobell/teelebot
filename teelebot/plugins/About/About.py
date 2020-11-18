# -*- coding:utf-8 -*-
import os

def About(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    bot_id = str(bot.getMe()["id"])
    prefix = "about"

    plugin_dir = bot.plugin_dir
    VERSION = bot.version

    if not os.path.exists(bot.path_converter(plugin_dir + "About/config.ini")):
        first_btn = ["交流群组", "https://t.me/teelebot_chat"]
        last_btn = ["项目地址", "https://github.com/plutobell/teelebot"]
    else:
        with open(bot.path_converter(plugin_dir + "About/config.ini"), 'r') as g:
            first_btn = g.readline().strip().split(',')
            last_btn = g.readline().strip().split(',')

    if text[1:len(prefix)+1] == prefix:
        inlineKeyboard = [
            [
                {"text": first_btn[0], "url": first_btn[1]},
                {"text": last_btn[0], "url": last_btn[1]},
            ]
        ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }
        status = bot.sendChatAction(chat_id, "typing")
        msg = "此 Bot 基于 <b>teelebot</b> 框架 <b>v" + VERSION + "</b>\n\n" +\
            "<b>teelebot</b> 是基于 Telegram Bot API 的 Bot 框架，具有插件系统，扩展方便。\n\n"

        req = bot.getUserProfilePhotos(user_id=str(bot_id), limit=1)
        if req.get("photos", "notphotos") != "notphotos":
            bot_icon = req.get("photos")[0][0]["file_id"]
            if type(bot_icon) == str and len(bot_icon) > 50:
                photo = bot_icon
            else:
                with open(bot.path_converter(plugin_dir + "About/icon.png"), "rb") as p:
                    photo = p.read()
        else:
            with open(bot.path_converter(plugin_dir + "About/icon.png"), "rb") as p:
                photo = p.read()

        status = bot.sendPhoto(chat_id=chat_id, photo=photo, caption=msg, parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)
        bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])

