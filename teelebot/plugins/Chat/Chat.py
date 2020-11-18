# -*- coding:utf-8 -*-
import requests
import urllib.parse as ubp
requests.adapters.DEFAULT_RETRIES = 5

def Chat(bot, message):
    plugin_dir = bot.plugin_dir

    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="
    hello = ("你好", "nihao", "hello", "Hello",
            "HELLO", "hi", "Hi", "HI",
            "早上好", "上午好", "下午好", "晚上好", "中午好",
            "good morning", "Good morning", "good afternoom",
            "Good afternoom", "good evening", "Good evening")
    if message["text"][1:] in hello:
        status = bot.sendChatAction(message["chat"]["id"], "typing")
        status = bot.sendVoice(message["chat"]["id"], voice=bot.path_converter(plugin_dir + "Chat/hello.ogg"),
            reply_to_message_id=message["message_id"])
    else:
        try:
            with requests.post(url + ubp.quote(message["text"][1:])) as req: #urlencode编码
                req.keep_alive = False
                req.encoding = "utf-8"
                if not req.status_code == requests.codes.ok:
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(chat_id=message["chat"]["id"], text="接口调用失败!",
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
                    bot.message_deletor(15, status["chat"]["id"], status["message_id"])
                else:
                    try:
                        msg = str(req.json().get("content").replace("{br}", "\n").replace("菲菲", "小埋"))
                        if "{face:" in msg:
                            msg = msg.split("}")[1]
                    except:
                        msg = "出错了."
                    status = bot.sendChatAction(message["chat"]["id"], "typing")
                    status = bot.sendMessage(message["chat"]["id"],text=msg,
                        parse_mode="HTML", reply_to_message_id=message["message_id"])
        except Exception as e:
            print(e)


def timer_func(bot, chat_id, message_id):
    status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)