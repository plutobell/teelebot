# -*- coding:utf-8 -*-
'''
creation time: 2020-3-21
last_modify: 2020-3-22
'''
import requests
from teelebot import Bot
from teelebot.handler import config

config = config()

#设置重连次数
requests.adapters.DEFAULT_RETRIES = 15

def Top(message):
    if str(message["from"]["id"]) != config["root"]:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "权限不足！", "html")
    elif str(message["from"]["id"]) == config["root"]:
        bot = Bot()

        url = ""
        data = {"Key" : ""}
        with open(bot.plugin_dir + "Top/key.ini", "r") as f:
            sets = f.readlines()
            url = sets[0].strip()
            data["Key"] = sets[1].strip()

        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "尊敬的主人，正在获取服务器信息，请稍等...", "html")
        req = requests.post(url=url, data=data)
        if req.json().get("status") == False:
            req.close()
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(message["chat"]["id"], "抱歉主人，获取服务器信息失败", "html")
        elif req.json().get("status") == True:
            contents = req.json().get("contents")
            Top = contents.get("Top")
            Cpu = contents.get("Cpu")
            Memory = contents.get("Memory")
            Swap = contents.get("Swap")

            top_time = Top["top_time"]
            top_up = Top["top_up"]
            cpu_id = Cpu["cpu_id"]
            memory_total = Memory["memory_total"]
            avail_memory = Swap["avail_memory"]
            Cpu_temperature = contents.get("Cpu_temperature")

            msg = "时间：" + str(top_time) + "%0A%0A" + \
            "系统已运行：" + str(top_up) + "%0A%0A" + \
            "CPU用量：" + "百分之" + str(round(100-float(cpu_id), 2)) + "已用，百分之" + str(float(cpu_id)) + "空闲%0A%0A" + \
            "内存用量：" + str(round(float(memory_total)-float(avail_memory), 2)) + "MiB已用，" + str(avail_memory) + "MiB空闲%0A%0A" + \
            "当前温度：" + str(Cpu_temperature) + "℃" + "%0A%0Av" + bot.VERSION

            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(message["chat"]["id"], msg, "html")