# -*- coding:utf-8 -*-
import requests

def TodayInHistory(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    prefix = "todayinhist"
    page_callback_command = "/" + prefix + "loadalldata"

    if "reply_markup" in message.keys():
        click_user_id = message["click_user"]["id"]
        from_user_id = message["reply_to_message"]["from"]["id"]
        callback_query_data = message["callback_query_data"]

        if callback_query_data[:len(page_callback_command)] == page_callback_command:
            if click_user_id == from_user_id:
                today_data = today_in_history()
                if today_data != False:
                    inlineKeyboard = [
                    [
                        {"text": "隐藏全部", "callback_data": "/todayinhisthidedata"},
                    ]
                    ]
                    reply_markup = {
                    "inline_keyboard": inlineKeyboard
                    }
                    msg = ""
                    for sec in today_data:
                        msg += "<i>" + str(sec["year"]) + "年</i> - " + str(sec["title"]) + "%0A%0A"
                    msg = "<b>历史上的今天: " + str(today_data[0]["today"]) + "</b>%0A%0A" + msg
                    status = bot.editMessageText(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="HTML", reply_markup=reply_markup)
                    status = bot.answerCallbackQuery(message["callback_query_id"])
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))
        elif callback_query_data[:len(page_callback_command)] == "/todayinhisthidedata":
            if click_user_id == from_user_id:
                today_data = today_in_history()
                if today_data != False:
                    inlineKeyboard = [
                    [
                        {"text": "加载全部", "callback_data": page_callback_command},
                    ]
                    ]
                    reply_markup = {
                    "inline_keyboard": inlineKeyboard
                    }
                    sec = today_data[0]
                    msg = "<b>历史上的今天: " + str(today_data[0]["today"]) + "</b>%0A%0A"
                    status = bot.editMessageText(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="HTML", reply_markup=reply_markup)
                    status = bot.answerCallbackQuery(message["callback_query_id"])
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))

    elif text[1:len(prefix)+1] == prefix:
        today_data = today_in_history()
        if today_data != False:
            inlineKeyboard = [
                [
                    {"text": "加载全部", "callback_data": page_callback_command},
                ]
            ]
            reply_markup = {
            "inline_keyboard": inlineKeyboard
            }
            msg = ""
            for sec in today_data[:5]:
                msg += "<i>" + str(sec["year"]) + "年</i> - " + str(sec["title"]) + "%0A%0A"
            msg = "<b>历史上的今天: " + str(today_data[0]["today"]) + "</b>%0A%0A" + msg + "..."
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)
            bot.message_deletor(60, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="获取数据失败，请重试!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])




def today_in_history():
    url = "https://api.asilu.com/today/"

    with requests.get(url=url, verify=False) as req:
        data = req.json()
        if not req.status_code == requests.codes.ok:
            return False
        elif data["code"] == 200:
            today_data = data["data"]
            today_data[0]["today"] = str(data["month"]) + "月" + str(data["day"]) + "日"
            return today_data
        else:
            return False