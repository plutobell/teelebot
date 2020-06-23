# -*- coding:utf-8 -*-
'''
creation time: 2020-5-28
last_modify: 2020-6-23
'''
import requests
import urllib.parse as ubp

def Translate(bot, message):
    prefix = "translate"

    if message["text"][1:len(prefix)+1] != prefix or len(message["text"].split(':')) != 2:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendMessage(message["chat"]["id"], "翻译失败！%0A请检查命令格式!", parse_mode="HTML", reply_to_message_id=message["message_id"])
        return False

    url = "http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i="
    words = ubp.quote(message["text"].split(':')[1])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
        "Host": "fanyi.youdao.com"
    }
    with requests.get(url + words, headers=headers) as req:#urlencode编码
        if not req.status_code == requests.codes.ok:
            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="获取失败，请重试!", parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        elif req.json().get("type", "UNSUPPORTED") == "UNSUPPORTED":  # 翻译的源文字未成功识别语言
            bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(chat_id=message["chat"]["id"], text="没看出来这是什么语言%0A%0A" + words, parse_mode="HTML", reply_to_message_id=message["message_id"])
            bot.message_deletor(15, message["chat"]["id"], status["message_id"])
        else:
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

            type_ = req.json().get("type")
            result = ""
            for paragraph in req.json().get("translateResult"):
                for sentence in paragraph:
                    result += sentence["tgt"]
                result += "%0A"

            status = bot.sendChatAction(message["chat"]["id"], "typing")
            status = bot.sendMessage(message["chat"]["id"], text="<b>" + types[type_] + "</b>%0A%0A" + result, parse_mode="HTML", reply_to_message_id=message["message_id"])
