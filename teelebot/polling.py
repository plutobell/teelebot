# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-23
@last modify: 2020-6-23
'''
import time
import sys

def runUpdates(bot):
        #print("debug=" + str(self.debug))
        plugin_list = bot.plugin_bridge.keys()
        while True:
            try:
                results = bot.getUpdates() #获取消息队列messages
                messages = bot._washUpdates(results)
                if messages == None or messages == False:
                    continue
                for message in messages: #获取单条消息记录message
                    bot._pluginRun(bot, message)
                time.sleep(0.2) #经测试，延时0.2s较为合理
            except KeyboardInterrupt: #判断键盘输入，终止循环
                sys.exit("程序终止") #退出存在问题，待修复