# -*- coding:utf-8 -*-

name = "teelebot"
__all__ = ['Bot']

from .teelebot import Bot
from .webhook import runWebhook
from .handler import config

bot = Bot()
config = config()

def main():
    if config["webhook"] == True:
        print(" * 正在自检", end="\r")
        status = bot.getWebhookInfo()
        url = "https://" + str(config["server_address"] + ":" +str(config["server_port"]) + "/bot" + str(config["key"]))
        if status != False:
            if status["url"] != url or status["has_custom_certificate"] == False:
                status = bot.setWebhook(url=url, certificate=config["cert_pub"])
                if status != True:
                    print("设置Webhook失败!")
                    return False
        else:
            print("获取运行模式失败!")

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + config["version"], "\n * 运行模式: Webhook\n")
        #webhook_app.debug=False
        runWebhook(host=config["local_address"], port=int(config["local_port"]))
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

        print(" * 机器人开始运行", "\n * 框架版本：teelebot v" + config["version"], "\n * 运行模式: getUpdates")
        bot._runUpdates()