# -*- coding:utf-8 -*-
"""
@creation date: 2019-8-23
@last modify: 2020-11-9
"""
from .polling import runUpdates
from .webhook import runWebhook
from .teelebot import Bot

name = "teelebot"
__all__ = ['Bot']

bot = Bot()

if bot.config["local_api_server"] != "False":
    api_server = "Local"
else:
    api_server = "Remote"


def main():
    print(" * 正在自检", end="\r")
    status = bot.getWebhookInfo()
    if not status:
        print("获取运行模式失败!")
        return False

    if bot.config["webhook"]:
        url = "https://" + str(bot.config["server_address"] + ":" + str(
            bot.config["server_port"]) + "/bot" + str(bot.config["key"]))
        if status["url"] != url or not status["has_custom_certificate"] or status["max_connections"] != int(
                bot.config["pool_size"]):
            status = bot.setWebhook(
                url=url, certificate=bot.config["cert_pub"], max_connections=bot.config["pool_size"])
            if not status:
                print("设置Webhook失败!")
                return False

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + bot.VERSION,
              "\n * 运行模式: Webhook", "\n * 最大线程: " + str(bot.config["pool_size"]),
              "\n * 连接地址: " + api_server + "\n")
        runWebhook(bot=bot, host=bot.config["local_address"], port=int(
            bot.config["local_port"]))

    else:
        if status["url"] != "" or status["has_custom_certificate"]:
            status = bot.deleteWebhook()
            if not status:
                print("设置getUpdates失败!")
                return False

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + bot.VERSION,
              "\n * 运行模式: Polling", "\n * 最大线程: " + str(bot.config["pool_size"]),
              "\n * 连接地址: " + api_server + "\n")
        runUpdates(bot=bot)
