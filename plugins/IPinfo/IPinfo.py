# -*- coding:utf-8 -*-
import requests

def IPinfo(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    gap= 30
    prefix = "ipinfo"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            ip = str(text.split(' ')[1])
            count = 0
            for i in ip.split('.'): #格式检查
                if len(i) > 3 or int(i) > 255 or int(i) < 0:
                    count += 1
            if len(ip.split('.')) not in [4, 8] or count != 0:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="地址格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
            elif len(ip.split('.')) in [4, 8]:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="正在查询，请稍等...", parse_mode="HTML", reply_to_message_id=message_id)
                txt_message_id = status["message_id"]

                result = ip_info(ip)
                if result != False:
                    msg = ""
                    for r in result.keys():
                        msg += str(r) + " : <i>" + str(result[r]) + "</i>%0A"
                    msg = "IP地址 <b>" + str(ip) + "</b> 的信息如下：%0A%0A" + msg
                    msg = msg.replace("country", "国家或地区")
                    msg = msg.replace("国家或地区Code", "国家或地区代码")
                    msg = msg.replace("region", "区域")
                    msg = msg.replace("区域Name", "区域名")
                    msg = msg.replace("city", "城市")
                    msg = msg.replace("zip", "邮政编码")
                    msg = msg.replace("lat", "纬度")
                    msg = msg.replace("lon", "经度")
                    msg = msg.replace("timezone", "时区")
                    msg = msg.replace("isp", "ISP")
                    status = bot.editMessageText(chat_id=chat_id, message_id=txt_message_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(60, chat_id, txt_message_id)
                else:
                    status = bot.editMessageText(chat_id=chat_id, message_id=txt_message_id, text="查询失败!", parse_mode="HTML")
                    bot.message_deletor(15, chat_id, txt_message_id)
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def ip_info(ip):
    url = "http://ip-api.com/json/"+ str(ip) + "?lang=zh-CN"
    with requests.post(url=url) as req:
        result = req.json()
        if not req.status_code == requests.codes.ok:
            return False
        elif result.get("status") == "success":
            del result["status"]
            del result["query"]
            del result["org"]
            del result["as"]
            return result
        else:
            return False

