# -*- coding:utf-8 -*-
import os
from teelebot import Bot

def Menu(message):
    bot = Bot()

    plugin_list = bot.plugin_bridge.values()
    menu_str = ""
    for plugin in plugin_list:
        with open(bot.plugin_dir + plugin + r"/__init__.py", encoding="utf-8") as f:
            line_1 = ""
            line_2 = ""
            for i in range(2):
                if i == 0:
                    line_1 = f.readline().strip()[1:]
                elif i == 1:
                    line_2 = f.readline().strip()[1:]
            menu_str += line_1 + " - " + line_2 + "%0A%0A"
    menu_str = "===== Command Menu =====%0A%0A" + menu_str + "%0A%0Av" + bot.VERSION
    status = bot.sendMessage(message["chat"]["id"], menu_str, "html")