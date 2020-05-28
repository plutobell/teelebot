# -*- coding:utf-8 -*-
'''
creation time: 2020-5-28
last_modify: 2020-5-28
'''
from teelebot import Bot
import requests
import urllib.parse as ubp

def Translate(message):
    bot = Bot()

    with open(bot.plugin_dir + "Translate/__init__.py", encoding="utf-8") as f:
        h = f.readline()[1:]
    if len(message["text"]) < len(h)+1:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "翻译失败！%0A要翻译的内容为空!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        return False
    elif message["text"][len(h)-1] != ':':
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "翻译失败！%0A请检查分隔符是否为' : '!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        return False

    url = "http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i="
    words = ubp.quote(message["text"][len(h):])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
        "Host": "fanyi.youdao.com"
    }
    req = requests.get(url + words, headers=headers) #urlencode编码
    types = {
        "ZH_CN2EN": "中文　»　英语",
        "ZH_CN2JA": "中文　»　日语",
        "ZH_CN2KR": "中文　»　韩语",
        "ZH_CN2FR": "中文　»　法语",
        "ZH_CN2RU": "中文　»　俄语",
        "ZH_CN2SP": "中文　»　西语",
        "EN2ZH_CN": "英语　»　中文",
        "JA2ZH_CN": "日语　»　中文",
        "KR2ZH_CN": "韩语　»　中文",
        "FR2ZH_CN": "法语　»　中文",
        "RU2ZH_CN": "俄语　»　中文",
        "SP2ZH_CN": "西语　»　中文"
    }

    type_= req.json().get("type")
    result = ""
    for paragraph in req.json().get("translateResult"):
        for sentence in paragraph:
            result += sentence["tgt"]
        result += "%0A"

    #print(type_, result)

    status = bot.sendChatAction(message["chat"]["id"], "typing")
    status = bot.sendMessage(message["chat"]["id"], text="<b>" + types[type_] + "</b>%0A%0A" + result, parse_mode="HTML", reply_to_message_id=message["message_id"])