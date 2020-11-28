# -*- coding:utf-8 -*-
'''
creation time: 2020-6-15
last_modify: 2020-11-28
'''
import os
from threading import Lock


lock = Lock()

def PluginCTL(bot, message):
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message["text"]
    prefix = "pluginctl"

    plugin_dir = bot.plugin_dir
    root_id = bot.root_id
    plugin_bridge = bot.plugin_bridge

    if not os.path.exists(bot.path_converter(plugin_dir + "PluginCTL/db/")):
        os.mkdir(bot.path_converter(plugin_dir + "PluginCTL/db/"))

    if message["chat"]["type"] != "private" and not os.path.exists(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db")):
        with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
            pass

    command = {
        "/pluginctlshow": "show",
        "/pluginctlon": "on",
        "/pluginctloff": "off"
    }
    count = 0
    for c in command.keys():
        if c in str(text):
            count += 1

    if message["chat"]["type"] != "private":
        admins = administrators(bot=bot, chat_id=chat_id)
        if str(root_id) not in admins:
            admins.append(str(root_id)) #root permission

    if message["chat"]["type"] == "private" and text[1:len(prefix)+1] == prefix: #判断是否为私人对话
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话.", parse_mode="text", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])
    elif text[1:len(prefix)+1] == prefix and count == 0:
        status = bot.sendChatAction(chat_id, "typing")
        msg = "<b>PluginCTL 插件功能</b>\n\n" +\
            "<b>/pluginctlshow</b> - 展示插件开启状态 \n" +\
            "<b>/pluginctlon</b> - 启用插件。格式：/pluginctlon接要启用的插件名，以空格分隔 \n" +\
            "<b>/pluginctloff</b> - 禁用插件。格式：/pluginctloff接要禁用的插件名，以空格分隔 \n" +\
            "<b>/pluginctlon all</b> - 启用所有插件 \n" +\
            "<b>/pluginctloff all</b> - 禁用所有插件，但必须的插件将被保留 \n" +\
            "<b>\n同时操作多个插件请用英文逗号分隔</b>\n"
        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])
        bot.message_deletor(30, chat_id, status["message_id"])
    elif "reply_markup" in message.keys():
        click_user_id = message["click_user"]["id"]
        from_user_id = message["reply_to_message"]["from"]["id"]
        callback_query_data = message["callback_query_data"]

        pluginctlsho_on_page = "/" + prefix + "showonpage"
        pluginctlsho_off_page = "/" + prefix + "showoffpage"

        plugin_dict = bot.plugin_bridge
        with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
            plugin_setting = f.read().strip()
        plugin_list_off = plugin_setting.split(',')
        plugin_list_on = {}
        for plugin in plugin_bridge.keys():
            if plugin not in plugin_list_off:
                plugin_list_on[plugin] = plugin_bridge[plugin]
        for key, val in plugin_list_on.items(): #dict.keys()不可修改！
            if val == "" or val == " ":
                plugin_list_on[key] = "nil"

        if callback_query_data == pluginctlsho_on_page:
            inlineKeyboard = [
                [
                    {"text": "禁用的", "callback_data": "/pluginctlshowoffpage"},
                ]
            ]
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }

            if click_user_id == from_user_id:
                for key, val in plugin_list_on.items(): #dict.keys()不可修改！
                    if val == "" or val == " ":
                        plugin_list_on[key] = "nil"
                msg_on = "<b>启用的插件</b> \n\n"
                for i, on in enumerate(plugin_list_on):
                    msg_on += " <b>[" + str(i+1) + "] " + str(on) + " " + str(plugin_list_on[on]) + "</b>\n"
                msg_on += "\n<b>nil</b> 代表指令为空"
                status = bot.editMessageText(chat_id=chat_id, message_id=message_id, text=msg_on + "\n", parse_mode="HTML", reply_markup=reply_markup)
                status = bot.answerCallbackQuery(message["callback_query_id"])
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))
        elif callback_query_data == pluginctlsho_off_page:
            inlineKeyboard = [
                [
                    {"text": "启用的", "callback_data": "/pluginctlshowonpage"},
                ]
            ]
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }

            if click_user_id == from_user_id:
                msg_off = "<b>禁用的插件</b> \n\n"
                for key, val in plugin_bridge.items(): #dict.keys()不可修改！
                    if val == "" or val == " ":
                        plugin_bridge[key] = "nil"
                for i, pluo in enumerate(plugin_list_off):
                    if pluo == "" or pluo == " ":
                        del plugin_list_off[i]
                if len(plugin_list_off) == 0:
                    msg_off += "无\n"
                else:
                    for i, off in enumerate(plugin_list_off):
                        msg_off += " <b>[" + str(i+1) + "] " + str(off) +  " " + str(plugin_bridge[off]) + "</b>\n"
                msg_off += "\n<b>nil</b> 代表指令为空"
                status = bot.editMessageText(chat_id=chat_id, message_id=message_id, text=msg_off + "\n", parse_mode="HTML", reply_markup=reply_markup)
                status = bot.answerCallbackQuery(message["callback_query_id"])
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))

    elif count > 0:
        if str(user_id) not in admins:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="抱歉，您无权操作.", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
        elif text[1:len(prefix + command["/pluginctlshow"])+1] == prefix + command["/pluginctlshow"]:
            inlineKeyboard = [
                [
                    {"text": "禁用的", "callback_data": "/pluginctlshowoffpage"},
                ]
            ]
            reply_markup = {
                "inline_keyboard": inlineKeyboard
            }

            plugin_dict = bot.plugin_bridge
            with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                plugin_setting = f.read().strip()
            plugin_list_off = plugin_setting.split(',')
            plugin_list_on = {}
            for plugin in plugin_bridge.keys():
                if plugin not in plugin_list_off:
                    plugin_list_on[plugin] = plugin_bridge[plugin]
            for key, val in plugin_list_on.items(): #dict.keys()不可修改！
                if val == "" or val == " ":
                    plugin_list_on[key] = "nil"
            msg_on = "<b>启用的插件</b> \n\n"
            for i, on in enumerate(plugin_list_on):
                msg_on += " <b>[" + str(i+1) + "] " + str(on) + " " + str(plugin_list_on[on]) + "</b>\n"
            msg_on += "\n<b>nil</b> 代表指令为空"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg_on + "\n", parse_mode="HTML", reply_to_message_id=message_id, reply_markup=reply_markup)
            bot.message_deletor(60, chat_id, status["message_id"])
        elif text[1:len(prefix + command["/pluginctlon"])+1] == prefix + command["/pluginctlon"]:
            plugin_list = list(plugin_bridge.keys())
            if len(text.split(' ')) == 2:
                plug_set = text.split(' ')[1]
                for p in plug_set.split(','):
                    if p == "nil":
                        p = ''
                    if p not in plugin_list:
                        if '' in plugin_list and p == ' ':
                            continue
                        if p == "all":
                            continue
                        msg = "插件 <b>" + str(p) + "</b> 不存在，请重试."
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return False
                if plug_set == "all":
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write('')
                    lock.release()
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="<b>已启用全部插件。</b>", parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return False
                elif len(plug_set.split(',')) >= 2:
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                        plugin_setting = f.read().strip()
                    plugin_list_off = plugin_setting.split(',')
                    for i, plug_s in enumerate(plug_set.split(',')):
                        if plug_s in plugin_list_off:
                            for i, p in enumerate(plugin_list_off):
                                if p == plug_s:
                                    del plugin_list_off[i]
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write(','.join(plugin_list_off))
                    lock.release()
                else:
                    plug_set = plug_set.strip()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                        plugin_setting = f.read().strip()
                    plugin_list_off = plugin_setting.split(',')
                    if plug_set in plugin_list_off:
                        for i, p in enumerate(plugin_list_off):
                            if p == plug_set:
                                del plugin_list_off[i]
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write(','.join(plugin_list_off))
                    lock.release()
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="<b>启用成功!</b>", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查.", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])

        elif text[1:len(prefix + command["/pluginctloff"])+1] == prefix + command["/pluginctloff"]:
            default_plugin = ["Menu", "About", "PluginCTL", "Uptime", "Schedule"]
            plugin_list = list(plugin_bridge.keys())
            if len(text.split(' ')) == 2:
                plug_set = text.split(' ')[1]
                for p in plug_set.split(','):
                    if p not in plugin_list:
                        if p == ' ' or p == '':
                            continue
                        if p == "all":
                            continue
                        msg = "插件 <b>" + str(p) + "</b> 不存在，请重试."
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)
                        bot.message_deletor(15, chat_id, status["message_id"])
                        return False
                if type(plug_set) == str and plug_set == "all":
                    plugin_list_alloff = []
                    for i, p in enumerate(plugin_list):
                        if p == "" or p == " ":
                            p = "nil"
                        if p not in default_plugin:
                            plugin_list_alloff.append(p)
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write(','.join(plugin_list_alloff))
                    lock.release()
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="<b>已禁用全部插件,\n但必须的插件仍被保留。</b>", parse_mode="HTML", reply_to_message_id=message_id)
                    bot.message_deletor(15, chat_id, status["message_id"])
                    return False
                elif len(plug_set.split(',')) >= 2:
                    for i, p in enumerate(plug_set.split(',')):
                        if p in default_plugin:
                            status = bot.sendChatAction(chat_id, "typing")
                            msg = "插件 <b>" + str(p) + "</b> 不支持禁用."
                            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)
                            bot.message_deletor(15, chat_id, status["message_id"])
                            return False
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                        plugin_setting = f.read().strip()
                    plugin_list_off = plugin_setting.split(',')
                    for i, plug_s in enumerate(plug_set.split(',')):
                        if plug_s not in plugin_list_off:
                            plugin_list_off.append(plug_s)
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write(','.join(plugin_list_off))
                    lock.release()
                else:
                    plug_set = plug_set.strip()
                    for i, p in enumerate(plug_set.split(',')):
                        if p in default_plugin:
                            status = bot.sendChatAction(chat_id, "typing")
                            msg = "插件 <b>" + str(p) + "</b> 不支持禁用."
                            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id)
                            bot.message_deletor(15, chat_id, status["message_id"])
                            return False
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "r") as f:
                        plugin_setting = f.read().strip()
                    plugin_list_off = plugin_setting.split(',')
                    if plug_set not in plugin_list_off:
                        plugin_list_off.append(plug_set)
                    lock.acquire()
                    with open(bot.path_converter(plugin_dir + "PluginCTL/db/" + str(chat_id) + ".db"), "w") as f:
                        f.write(','.join(plugin_list_off))
                    lock.release()
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="<b>禁用成功!</b>", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查.", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])


    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查.", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])



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
