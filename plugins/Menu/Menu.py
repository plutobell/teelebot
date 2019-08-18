# -*- coding:utf-8 -*-
import sys, os
sys.path.append("../")
from TeeleBot import teelebot
from config import config

def Menu(message):
    plugin_list = []
    menu_str = ""
    plugin_lis = os.listdir(r"plugins/")
    for plugi in plugin_lis:
        if os.path.isdir(r"plugins/" + plugi):
            plugin_list.append(plugi)
    for plugin in plugin_list:
        with open(r"plugins/" + plugin + r"/__init__.py", encoding="utf-8") as f:
            line_1 = ""
            line_2 = ""
            for i in range(2):
                if i == 0:
                    line_1 = f.readline().strip()[1:]
                elif i == 1:
                    line_2 = f.readline().strip()[1:]
            menu_str += line_1 + " - " + line_2 + "%0A%0A"
    menu_str = "===== Command Menu =====%0A%0A" + menu_str + "%0A%0Av" + config["version"]
    bot = teelebot.Bot()
    status = bot.sendMessage(message["chat"]["id"], menu_str, "html")