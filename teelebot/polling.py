# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-23
@last modify: 2020-11-19
'''
import time
import sys


def _runUpdates(bot):
    plugin_bridge = bot.plugin_bridge
    plugin_list = plugin_bridge.keys()
    while True:
        try:
            results = bot.getUpdates()  # 获取消息队列messages
            messages = bot._washUpdates(results)
            if messages is None or not messages:
                continue
            for message in messages:  # 获取单条消息记录message
                bot._pluginRun(bot, message)
        except KeyboardInterrupt:
            sys.exit("Bot Exit.")  # 退出存在问题，待修复
