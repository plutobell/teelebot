# -*- coding:utf-8 -*-
'''
creation time: 2020-5-28
last_modify: 2020-5-29
'''

from teelebot import Bot
from collections import defaultdict
import re

def Guard(message):
    bot = Bot()
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]

    if "new_chat_members" in message.keys():
        new_chat_members = message["new_chat_members"]

        DFA = DFAFilter()
        DFA.parse(bot.plugin_dir + "Guard/keywords")
        for new_chat_member in new_chat_members:
            user_id = str(new_chat_member["id"])
            first_name = new_chat_member["first_name"].strip()
            #print("New Member：", user_id, first_name)
            repl = "<*>"
            result = DFA.filter(first_name, repl)
            if repl in result or len(first_name) > 25:
                status = bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=30)
                status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                msg = "由于用户 <b>" + user_id + "</b> 的名字过于优美，小埋无法识别%0A<b>Ta</b>永远地离开了我们。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML")
            else:
                msg = "欢迎你，<b>" + first_name + "</b>%0A我是滥权Bot <b>小埋</b>，发送 <b>/start</b> 获取帮助。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML")
            status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
    elif "left_chat_member" in message.keys():
        status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)







class DFAFilter():

    '''Filter Messages from keywords

    Use DFA to keep algorithm perform constantly

    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='UTF-8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)


if __name__ == "__main__":
    gl = DFAFilter()
    gl.parse("keywords")
    import time
    t = time.time()
    print (gl.filter("免费出售", "*"))
    print (time.time() - t)