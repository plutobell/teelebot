# -*- coding:utf-8 -*-
import requests

def Whois(bot, message):
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    txt_message_id = 0
    gap= 30
    prefix = "whois"

    if text[1:len(prefix)+1] == prefix:
        if len(text.split(' ')) == 2:
            domain = str(text.split(' ')[1])
            if len(domain.split('.')) > 1 and len(domain.split('.')) <= 2:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="正在查询，请稍等...", parse_mode="HTML", reply_to_message_id=message_id)
                txt_message_id = status["message_id"]

                result = whois_info(domain=domain)
                if result != False:
                    msg = ""
                    for r in result.keys():
                        msg += str(r) + " : <i>" + str(result[r]) + "</i>%0A"
                    msg = "域名 <b>" + str(domain) + "</b> 的Whois信息如下：%0A%0A" + msg
                    msg = msg.replace("is_reg", "是否注册")
                    msg = msg.replace("domain", "域名")
                    msg = msg.replace("suffix", "后缀")
                    msg = msg.replace("whois_server", "whois服务器")
                    msg = msg.replace("creation_date", "创建日期")
                    msg = msg.replace("expiration_date", "到期日期")
                    msg = msg.replace("registrar", "注册商")
                    msg = msg.replace("registrant_email", "注册人电子邮件")
                    msg = msg.replace("registrant_phone", "注册人电话号码")
                    msg = msg.replace("nomain_status", "Nomain状态")
                    msg = msg.replace("name_server", "域名服务器")
                    msg = msg.replace("dnssec", "DNSSec")
                    msg = msg.replace("[", "")
                    msg = msg.replace("]", "")
                    msg = msg.replace("'", "")
                    status = bot.editMessageText(chat_id=chat_id, message_id=txt_message_id, text=msg, parse_mode="HTML")
                    bot.message_deletor(60, chat_id, txt_message_id)
                else:
                    status = bot.editMessageText(chat_id=chat_id, message_id=txt_message_id, text="查询失败!", parse_mode="HTML")
                    bot.message_deletor(15, chat_id, txt_message_id)
            else:
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text="域名格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
                bot.message_deletor(15, chat_id, status["message_id"])
        else:
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text="指令格式错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(15, chat_id, status["message_id"])
    else:
        status = bot.sendChatAction(chat_id, "typing")
        status = bot.sendMessage(chat_id=chat_id, text="指令错误，请检查!", parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(15, chat_id, status["message_id"])


def whois_info(domain):
    url = "https://v1.alapi.cn/api/whois?domain="+ str(domain)
    with requests.post(url=url) as req:
        result = req.json()
        if not req.status_code == requests.codes.ok:
            return False
        elif result.get("msg") == "success":
            return result["data"]
        else:
            return False

