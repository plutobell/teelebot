# -*- coding:utf-8 -*-

name = "teelebot"
__all__ = ['Bot']

from .teelebot import Bot
from .webhook import runWebhook
from .polling import runUpdates

bot = Bot()

def main():
    if bot.config["webhook"] == True:
        print(" * 正在自检", end="\r")
        status = bot.getWebhookInfo()
        url = "https://" + str(bot.config["server_address"] + ":" +str(bot.config["server_port"]) + "/bot" + str(bot.config["key"]))
        if status != False:
            if status["url"] != url or status["has_custom_certificate"] == False or status["max_connections"] != int(bot.config["pool_size"]):
                status = bot.setWebhook(url=url, certificate=bot.config["cert_pub"], max_connections=bot.config["pool_size"])
                if status != True:
                    print("设置Webhook失败!")
                    return False
        else:
            print("获取运行模式失败!")

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + bot.VERSION, "\n * 运行模式: Webhook", "\n * 最大线程: " + str(bot.config["pool_size"]))
        runWebhook(bot=bot, host=bot.config["local_address"], port=int(bot.config["local_port"]))
    else:
        print(" * 正在自检", end="\r")
        status = bot.getWebhookInfo()
        if status != False:
            if status["url"] != "" or status["has_custom_certificate"] != False:
                status = bot.deleteWebhook()
                if status != True:
                    print("设置getUpdates失败!")
                    return False
        else:
            print("获取运行模式失败!")

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + bot.VERSION, "\n * 运行模式: getUpdates", "\n * 最大线程: " + str(bot.config["pool_size"]))
        runUpdates(bot=bot)