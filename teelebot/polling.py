# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-23
@last modify: 2020-12-12
'''
import time
import os
import signal


def _runUpdates(bot):
    plugin_bridge = bot.plugin_bridge
    plugin_list = plugin_bridge.keys()

    signal.signal(signal.SIGINT, __exit)
    while True:
        results = bot.getUpdates()  # 获取消息队列messages
        messages = bot._washUpdates(results)
        if messages is None or not messages:
            continue
        for message in messages:  # 获取单条消息message
            bot._pluginRun(bot, message)


def __exit(signum, frame):
    print("Bot Exit.")
    os._exit(0)


