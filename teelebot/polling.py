# -*- coding:utf-8 -*-
'''
@creation date: 2020-06-23
@last modify: 2021-03-10
'''
import time
import os
import signal


def _runUpdates(bot):

    signal.signal(signal.SIGINT, __exit)
    while True:
        results = bot.getUpdates(allowed_updates=bot._allowed_updates)  # 获取消息队列messages
        messages = bot._washUpdates(results)
        if messages is None or not messages:
            continue
        for message in messages:  # 获取单条消息message
            bot._pluginRun(bot, message)


def __exit(signum, frame):
    print("Bot Exit.")
    os._exit(0)


