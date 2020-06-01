# -*- coding:utf-8 -*-
'''
creation time: 2020-5-28
last_modify: 2020-6-1
'''

from teelebot import Bot
from collections import defaultdict
import re
import string
from teelebot.handler import config
from captcha.image import ImageCaptcha
from random import randint
from io import BytesIO

config = config()
bot = Bot()

def Guard(message):
    repl = "<*>"
    DFA = DFAFilter()
    DFA.parse(bot.plugin_dir + "Guard/keywords")
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]

    if "new_chat_members" in message.keys():
        new_chat_members = message["new_chat_members"]

        for new_chat_member in new_chat_members:
            user_id = str(new_chat_member["id"])
            if "first_name" in new_chat_member.keys(): #Optional (first_name or last_name)
                first_name = new_chat_member["first_name"].strip()
            else:
                first_name = ""
            if "last_name" in new_chat_member.keys():
                last_name = new_chat_member["last_name"].strip()
            else:
                last_name = ""
            name = str(first_name + last_name).strip()
            #print("New Member：", user_id, first_name)
            result = DFA.filter(name, repl)
            if (repl in result and len(name) > 9) or (len(name) > 25):
                status = bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=60)
                status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
                msg = "由于用户 <b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b> 的名字<b> 过于优美</b>，无法识别，Ta永远地离开了我们。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            else:
                status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b> 欢迎加入，发送 <b>/start</b> 获取帮助。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
    elif "left_chat_member" in message.keys():
        user_id = message["left_chat_member"]["id"]
        if "first_name" in message["left_chat_member"]:
            first_name = message["left_chat_member"]["first_name"].strip()
        else:
            first_name = ""
        if "last_name" in message["left_chat_member"]:
            last_name = message["left_chat_member"]["last_name"].strip()
        else:
            last_name = ""
        name = str(first_name + last_name).strip()

        result = DFA.filter(first_name, repl)
        if (repl in result and len(name) > 9) or (len(name) > 25):
            status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        else:
            status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
            msg = "用户 <b><a href='tg://user?id="+ str(user_id) + "'>"+ first_name + " " + last_name +"</a></b> 离开了我们。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
    elif "text" in message.keys():
        text = message["text"]
        prefix = "guard"
        admins = []
        if (message["chat"]["type"] == "private") and (text[1:len(prefix)+1] == prefix): #判断是否为私人对话
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话!", parse_mode="text", reply_to_message_id=message["message_id"])
            return False
        elif text[1:len(prefix)+1] == prefix:
            admins = administrators(chat_id=chat_id)
            if str(config["root"]) not in admins:
                admins.append(str(config["root"])) #root permission

        if (text[1:] == prefix) or (text[1:len(prefix)+2] == prefix + '@'):
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="<b>===== Guard 插件功能 =====</b>%0A%0A<b>/guardadd</b> - 添加过滤关键词。格式:命令加空格加关键词，多个关键词之间用英文逗号隔开%0A", parse_mode="HTML", reply_to_message_id=message["message_id"])
        elif (str(message["from"]["id"]) not in admins) and (text[1:len(prefix)+1] == prefix): #判断有无权限操作
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id, "抱歉，您没有权限!", parse_mode="text", reply_to_message_id=message["message_id"])
        elif text[1:len(prefix)+1] == prefix:
            if text[1:] == prefix + "add":
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id, "添加失败！%0A关键字为空!", parse_mode="text", reply_to_message_id=message["message_id"])
            elif ("，" in text[1:]) or (text[1:len(prefix + "add")+2] == prefix + "add" + '@'):
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id, "添加失败！%0A请检查命令格式!", parse_mode="text", reply_to_message_id=message["message_id"])
            elif text[1:len("guard")+5] == prefix + "add" + " ":
                text_sp = text[1:].split(" ")
                if len(text_sp) != 2:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id, "添加失败！%0A请检查命令格式!", parse_mode="text", reply_to_message_id=message["message_id"])
                else:
                    if "," in text_sp[1]:
                        switch = 0
                        keywords = text_sp[1].split(',')
                        from collections import Counter
                        keyword_count = Counter(keywords)
                        for keyw_c in keyword_count.keys(): #关键词重复检测
                            if keyword_count[keyw_c] != 1:
                                status = bot.sendChatAction(chat_id, "typing")
                                status = bot.sendMessage(chat_id, "添加失败！%0A存在重复的关键字!", parse_mode="text", reply_to_message_id=message["message_id"])
                                return False

                        before_count = len(keywords)
                        if len(keywords) > 5: #最多同时录入5个关键词
                            status = bot.sendChatAction(chat_id, "typing")
                            status = bot.sendMessage(chat_id, "添加失败！%0A最多只支持5个!", parse_mode="text", reply_to_message_id=message["message_id"])
                            return False
                    else:
                        switch = 1
                        keyword = text_sp[1].strip()
                        before_count = 1

                    if switch == 0: #判断要存入的关键词是否已经存在
                        keywords_wash = []
                        for keyw in keywords:
                            result = DFA.filter(keyw, repl)
                            if repl not in result:
                                keywords_wash.append(keyw)
                        if len(keywords_wash) == 0:
                            keywords = None
                            after_count = 0
                        else:
                            keywords = keywords_wash
                            after_count = len(keywords)
                    elif switch == 1:
                        result = DFA.filter(keyword, repl)
                        if repl not in result:
                            keyword = None
                            after_count = 0
                        else:
                            after_count = 1

                    keys = "" #成功添加的关键字统计
                    with open(bot.plugin_dir + "Guard/keywords", "a", encoding="utf-8") as k:
                        if switch == 0:
                            if keywords == None:
                                status = bot.sendChatAction(chat_id, "typing")
                                status = bot.sendMessage(chat_id, "您输入的 " + str(before_count) +" 个关键词已经存在于库中!", parse_mode="text", reply_to_message_id=message["message_id"])
                                return False
                            else:
                                for keyw in keywords:
                                    k.write("\n" + keyw.strip())
                                    keys += keyw + "%0A"

                        elif switch == 1:
                            if keyword == None:
                                status = bot.sendChatAction(chat_id, "typing")
                                status = bot.sendMessage(chat_id, "您输入的 " + str(before_count) +" 个关键词已经存在于库中!", parse_mode="text", reply_to_message_id=message["message_id"])
                                return False
                            else:
                                k.write("\n" + keyword)
                                keys += keyword + "%0A"
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id, "成功添加 " + str(after_count) +" 个关键词%0A剩余的 " + str(int(before_count)-int(after_count)) + " 个关键词已经存在于库中。%0A成功添加的关键词有：%0A%0A" + str(keys), parse_mode="text", reply_to_message_id=message["message_id"])


def administrators(chat_id):
    admins = []
    results = bot.getChatAdministrators(chat_id=chat_id)
    if results != False:
        for result in results:
            if str(result["user"]["is_bot"]) == "False":
                admins.append(str(result["user"]["id"]))
    else:
        admins = False

    return admins


def captcha_img(width=320, height=120, font_sizes=(100, 110, 120, 200, 210, 220), fonts=None):

    captcha_len = 5
    captcha_range = string.digits + string.ascii_letters
    captcha_range_len = len(captcha_range)
    captcha_text = ""
    for i in range(captcha_len):
        captcha_text += captcha_range[randint(0, captcha_range_len-1)]

    img = ImageCaptcha(width=width, height=height, font_sizes=font_sizes)
    image = img.generate_image(captcha_text)

    #save to bytes
    bytes_image= BytesIO()
    image.save(bytes_image, format='png')
    bytes_image= bytes_image.getvalue()

    return bytes_image, captcha_text


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