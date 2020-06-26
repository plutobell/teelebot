# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-23
@last modify: 2020-6-26
'''
import time
import sys

def runUpdates(bot):
        plugin_list = bot.plugin_bridge.keys()
        while True:
            try:
                results = bot.getUpdates() #获取消息队列messages
                messages = bot._washUpdates(results)
                if messages == None or messages == False:
                    continue
                for message in messages: #获取单条消息记录message
                    bot._pluginRun(bot, message)
            except KeyboardInterrupt:
                sys.exit("程序终止") #退出存在问题，待修复