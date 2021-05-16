# -*- coding:utf-8 -*-
"""
@creation date: 2019-08-23
@last modify: 2021-04-26
"""
import os
import requests
import urllib3

from .polling import _runUpdates
from .webhook import _runWebhook
from .teelebot import Bot

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

name = "teelebot"
__all__ = ['Bot']

bot = Bot()
VERSION = bot.version

if bot._local_api_server != "False":
    api_server = "Local"
else:
    api_server = "Remote"


def main():
    print(
        "    __            __     __          __  " + "\n" + \
        "   / /____  ___  / /__  / /_  ____  / /_ " + "\n" + \
        "  / __/ _ \/ _ \/ / _ \/ __ \/ __ \/ __/ " + "\n" + \
        " / /_/  __/  __/ /  __/ /_/ / /_/ / /_   " + "\n" + \
        " \__/\___/\___/_/\___/_.___/\____/\__/   " + "\n"
    )
    print(" * Self-checking...", end="\r")
    req = requests.post(url=bot._url + "getWebhookInfo", verify=False)
    if not req.json().get("ok"):
        if (req.json().get("error_code") == 401 and
            req.json().get("description") == "Unauthorized"):
            print("\nif you already logout the bot from the cloud Bot API server,please wait at least 10 minutes and try again.")
        else:
            print("\nfailed to get running mode!")
        os._exit(0)

    status = req.json().get("result")
    pending_update_count = status["pending_update_count"]
    allowed_updates = status.get("allowed_updates", [])

    if bot._webhook:
        protocol = "https://"
        if bot._local_api_server != "False":
            protocol = "http://"
        url = protocol + str(bot._server_address + ":" + str(
            bot._server_port) + "/bot" + str(bot._key))
        if (bot._drop_pending_updates == True and pending_update_count != 0) \
            or (status["url"] != url) or (status["has_custom_certificate"] != bot._self_signed) \
            or status["max_connections"] != int(bot._pool_size) \
            or allowed_updates != bot._allowed_updates:
            if bot._self_signed:
                status = bot.setWebhook(
                    url=url,
                    certificate=bot._cert_pub,
                    max_connections=bot._pool_size,
                    allowed_updates=bot._allowed_updates,
                    drop_pending_updates=bot._drop_pending_updates
                )
            else:
                status = bot.setWebhook(
                    url=url,
                    max_connections=bot._pool_size,
                    allowed_updates=bot._allowed_updates,
                    drop_pending_updates=bot._drop_pending_updates
                )

            if not status:
                print("\nfailed to set Webhook!")
                os._exit(0)

        print(" * The teelebot starts running",
              "\n * Version : v" + VERSION,
              "\n *    Mode : Webhook",
              "\n *  Thread : " + str(bot._pool_size),
              "\n *  Server : " + api_server + "\n")
        _runWebhook(bot=bot,
            host=bot._local_address,port=int(bot._local_port))

    else:
        if status["url"] != "" or status["has_custom_certificate"]:
            status = bot.deleteWebhook()
            if not status:
                print("\nfailed to set getUpdates!")
                os._exit(0)

        print(" * The teelebot starts running",
              "\n * Version : v" + VERSION,
              "\n *    Mode : Polling",
              "\n *  Thread : " + str(bot._pool_size),
              "\n *  Server : " + api_server + "\n")
        if bot._drop_pending_updates == True and \
            pending_update_count != 0:
            results = bot.getUpdates(allowed_updates=bot._allowed_updates)
            messages = bot._washUpdates(results)
        _runUpdates(bot=bot)
