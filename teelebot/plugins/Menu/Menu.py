# -*- coding:utf-8 -*-
'''
creation time: 2019-8-15
last_modify: 2020-6-23
'''
import os

def Menu(bot, message):
    prefix = "start"
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    chat_type = message["chat"]["type"]

    plugin_list = bot.plugin_bridge.values()
    if chat_type != "private" and "/pluginctl" in bot.plugin_bridge.keys() and bot.plugin_bridge["/pluginctl"] == "PluginCTL":
        if os.path.exists(bot.plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"):
            with open(bot.plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db", "r") as f:
                plugin_setting = f.read().strip()
            plugin_list_off = plugin_setting.split(',')
            plugin_list_value = {}
            for plug in bot.plugin_bridge.keys():
                plugin_temp = plug
                if plug == "" or plug == " ":
                    plug = "nil"
                if plug not in plugin_list_off:
                    plug = plugin_temp
                    plugin_list_value[plug] = bot.plugin_bridge[plug]
            plugin_list = plugin_list_value.values()

    plugin_count = len(plugin_list)
    page_size = 5
    page_total = int((plugin_count + page_size - 1) / page_size) # 总页数=（总数+每页数量-1）/每页数量
    page_callback_command = "/" + prefix + "page?page="
    with open(bot.plugin_dir + "Menu/config.ini", 'r', encoding="utf-8") as g:
        first_btn = g.readline().strip().split(',')
        last_btn = g.readline().strip().split(',')

    wait_time = plugin_count * 7

    if "reply_markup" in message.keys():
        click_user_id = message["click_user"]["id"]
        from_user_id = message["reply_to_message"]["from"]["id"]
        callback_query_data = message["callback_query_data"]

        if callback_query_data[:len(page_callback_command)] == page_callback_command:
            if click_user_id == from_user_id:
                page = int(callback_query_data.split('=')[1])
                page, menu_str = menu_text(bot, page=page, page_total=page_total, page_size=page_size, plugin_list=plugin_list)
                previous_page = page - 1
                if previous_page < 1:
                    previous_page = 1
                next_page = page + 1
                if next_page > page_total:
                    next_page = page_total

                if page_total == 1:
                    inlineKeyboard = [
                        [
                            {"text": first_btn[0], "url": first_btn[1]},
                            {"text": last_btn[0], "url": last_btn[1]},
                        ]
                    ]
                elif page == 1:
                    inlineKeyboard = [
                        [
                            {"text": first_btn[0], "url": first_btn[1]},
                            {"text": "下一页", "callback_data": page_callback_command + str(page+1)},
                        ]
                    ]
                elif page == page_total:
                    inlineKeyboard = [
                        [
                            {"text": "上一页", "callback_data": page_callback_command + str(page-1)},
                            {"text": last_btn[0], "url": last_btn[1]},
                        ]
                    ]
                else:
                    inlineKeyboard = [
                        [
                            {"text": "上一页", "callback_data": page_callback_command + str(previous_page)},
                            {"text": "下一页", "callback_data": page_callback_command + str(next_page)},
                        ]
                    ]
                reply_markup = {
                    "inline_keyboard": inlineKeyboard
                }
                status = bot.editMessageText(chat_id=chat_id, message_id=message_id, text=menu_str, parse_mode="HTML", reply_markup=reply_markup)
                status = bot.answerCallbackQuery(message["callback_query_id"])
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))
    else:
        page = 1
        if page_total == 1:
            inlineKeyboard = [
                [
                    {"text": first_btn[0], "url": first_btn[1]},
                    {"text": last_btn[0], "url": last_btn[1]},
                ]
            ]
        else:
            inlineKeyboard = [
                [
                    {"text": first_btn[0], "url": first_btn[1]},
                    {"text": "下一页", "callback_data": page_callback_command + str(page+1)},
                ]
            ]
        reply_markup = {
            "inline_keyboard": inlineKeyboard
        }

        page, menu_str = menu_text(bot=bot, page=page, page_total=page_total, page_size=page_size, plugin_list=plugin_list)

        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text=menu_str, parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)

        bot.message_deletor(wait_time, message["chat"]["id"], status["message_id"])

def menu_text(bot, page, page_total, page_size, plugin_list):

    if page < 1:
        page = 1
    elif page > page_total:
        page = page_total

    if page >=1 and page <= page_total:
        menu_str = ""
        plugin_range = range(page*page_size-page_size, page*page_size-1+1)
        for i, plugin in enumerate(plugin_list): #(now_page*page_size-page_size,now_page*page_size-1)
            if i in plugin_range:
                with open(bot.plugin_dir + plugin + r"/__init__.py", encoding="utf-8") as f:
                    line_1 = ""
                    line_2 = ""
                    for i in range(2):
                        if i == 0:
                            line_1 = f.readline().strip()[1:]
                        elif i == 1:
                            line_2 = f.readline().strip()[1:]
                    menu_str += "<b>" + line_1 + "</b> - " + line_2 + "%0A%0A"
        menu_str = "<b>===== 插件列表 [" + str(page) + "/" + str(page_total) + "] =====</b>%0A%0A" + menu_str + "%0A<b><i>v" + bot.VERSION + "</i></b>"

        return page, menu_str
