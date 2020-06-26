# -*- coding:utf-8 -*-

def ID(bot, message):
    bot_id = bot.key.split(':')[0]
    if "reply_to_message" not in message.keys():
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        if str(message["from"]["id"]) == bot.config["root"]:
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(message["chat"]["id"], "主人%0A" + "您的用户ID为：<b>" + str(message["from"]["id"]) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
        else:
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(message["chat"]["id"], str(message["from"]["first_name"]) + "%0A您的用户ID为：<b>" + str(message["from"]["id"]) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    elif "reply_to_message" in message.keys() and message["chat"]["type"] != "private":
        admins = administrators(bot, message["chat"]["id"])

        if message["chat"]["type"] != "private":
            admins = administrators(bot=bot, chat_id=message["chat"]["id"])
            if str(bot.config["root"]) not in admins:
                admins.append(str(bot.config["root"])) #root permission

        if str(message["from"]["id"]) in admins:
            reply_to_message = message["reply_to_message"]
            target_message_id = reply_to_message["message_id"]
            target_user_id = reply_to_message["from"]["id"]
            target_chat_id = reply_to_message["chat"]["id"]

            if str(bot_id) != str(target_user_id):
                if str(message["from"]["id"]) == bot.config["root"]:
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(message["chat"]["id"], "主人%0A您查询的用户的ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                else:
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(message["chat"]["id"], str(message["from"]["first_name"]) + "%0A您查询的用户的ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
            else:
                if str(message["from"]["id"]) == bot.config["root"]:
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(message["chat"]["id"], "主人，我的ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
                else:
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", parse_mode="text", reply_to_message_id=message["message_id"])
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", parse_mode="text", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
    elif "reply_to_message" in message.keys() and message["chat"]["type"] == "private":
        reply_to_message = message["reply_to_message"]
        target_message_id = reply_to_message["message_id"]
        target_user_id = reply_to_message["from"]["id"]
        target_chat_id = reply_to_message["chat"]["id"]

        if str(bot_id) == str(target_user_id):
            if str(message["from"]["id"]) == bot.config["root"]:
                status = bot.sendChatAction(message["chat"]["id"], "typing")
                status = bot.sendMessage(message["chat"]["id"], "主人，我的ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            else:
                status = bot.sendChatAction(message["chat"]["id"], "typing")
                status = bot.sendMessage(chat_id=message["chat"]["id"], text="抱歉，您无权查询!", parse_mode="text", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            if str(message["from"]["id"]) == bot.config["root"]:
                status = bot.sendChatAction(message["chat"]["id"], "typing")
                status = bot.sendMessage(message["chat"]["id"], "主人%0A您查询的用户的ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            elif message["chat"]["id"] == target_user_id:
                status = bot.sendChatAction(message["chat"]["id"], "typing")
                status = bot.sendMessage(message["chat"]["id"], str(message["from"]["first_name"]) + "%0A您的用户ID为：<b>" + str(target_user_id) + "</b>", parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

def administrators(bot, chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
    else:
        admins = False

    return admins
