# -*- coding:utf-8 -*-
'''
creation time: 2020-11-11
last_modify: 2020-11-14
'''
import time

def Schedule(bot, message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    message_id = message["message_id"]
    text = message["text"]

    root_id = bot.root_id

    gaps = {
        "1s": 1,
        "2s": 2,
        "5s": 5,
        "10s": 10,
        "15s": 15,
        "30s": 30,
        "45s": 45,

        "1m": 60,
        "2m": 120,
        "5m": 300,
        "10m": 600,
        "15m": 900,
        "30m": 1800,
        "45m": 2700,

        "1h": 3600,
        "2h": 7200,
        "4h": 10800,
        "6h": 21600,
        "8h": 28800,
        "10h": 36000,
        "12h": 43200,

        "1d": 86400,
        "3d": 259200,
        "5d": 432000,
        "7d": 604800,
        "10d": 864000,
        "15d": 1296000,
        "20d": 1728000,
        "30d": 2592000
    }

    prefix = "/sched"
    command = { #命令注册
            "/schedadd": "add",
            "/scheddel": "del",
            "/schedfind": "find",
            "/schedclear": "clear",
            "/schedstatus": "status"
        }
    count = 0
    for c in command.keys():
        if c in str(text):
            count += 1

    if text.split(" ")[0] != prefix and prefix in text and str(user_id) != root_id:
        status = bot.sendMessage(chat_id, text="<b>无权限</b>", parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(15, status["chat"]["id"], status["message_id"])
        return

    if text[:len(prefix)] == prefix and count == 0:
        msg = "<b>Schedule 插件功能</b>" + "\n\n" + \
            "<b>/schedadd</b> 添加任务 格式：指令+空格+周期+消息" + "\n" + \
            "<b>/scheddel</b> 移除任务 格式：指令+空格+标识" + "\n" + \
            "<b>/schedfind</b> 查找任务 格式：指令+空格+标识" + "\n" + \
            "<b>/schedclear</b> 移除所有任务" + "\n" + \
            "<b>/schedstatus</b> 查看队列信息" + "\n\n" + \
            "<i>支持的周期指令：1s 2s 5s 10s 15s 30s 45s | "+ \
            "1m 2m 5m 10m 15m 30m 45m | " + \
            "1h 2h 4h 6h 8h 10h 12h | " + \
            "1d 3d 5d 7d 10d 15d 20d 30d" + "</i>"
        status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
            reply_to_message_id=message_id)
        bot.message_deletor(60, status["chat"]["id"], status["message_id"])

    elif text[:len(prefix + "add")] == prefix + "add":
        if  len(text.split(" ")) == 3:
            msg = ""
            gap_key = str(text.split(" ")[1])
            if gap_key not in gaps.keys():
                msg = "<b>错误的周期，支持的周期指令：</b> \n\n" + \
                    "<b>1s 2s 5s 10s 15s 30s 45s \n" + \
                    "1m 2m 5m 10m 15m 30m 45m \n" + \
                    "1h 2h 4h 6h 8h 10h 12h \n" + \
                    "1d 3d 5d 7d 10d 15d 20d 30d" + "</b>"
                status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
                    reply_to_message_id=message_id)
                bot.message_deletor(30, status["chat"]["id"], status["message_id"])
                return

            gap = gaps[gap_key]
            gap_key = gap_key.replace("s", "秒").replace("m", "分钟").replace("h", "小时").replace("d", "天")
            msg = str(text.split(" ")[2]) + "\n\n" + "<code>此消息为定时发送，周期" + str(gap_key) + "</code>"
            ok, uid = bot.schedule.add(gap, event, (bot, message["chat"]["id"], msg, "HTML"))
            timestamp = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
            if ok:
                msg = "<b>任务已加入队列</b>\n\n" + \
                    "周期: <code>" + gap_key + "</code>\n" + \
                    "目标: <code>" + str(chat_id) + "</code>\n" + \
                    "标识: <code>" + str(uid) + "</code>\n" + \
                    "时间: <code>" + str(timestamp) + "</code>\n\n" + \
                    "<code>此消息将在<b>60秒</b>后销毁，请尽快保存标识</code>\n"
            else:
                msg = ""
                if uid == "Full":
                    msg = "<b>队列已满</b>"
                else:
                    msg = "<b>遇到错误</b> \n\n <i>" + uid + "</i>"
            status = bot.sendMessage(chat_id, text=msg, parse_mode="HTML",
                reply_to_message_id=message_id)
            bot.message_deletor(60, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + "add gap text)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text[:len(prefix + "del")] == prefix + "del":
        if len(text.split(" ")) == 2:
            msg = ""
            uid = str(text.split(" ")[1])
            ok, uid = bot.schedule.delete(uid)
            if ok:
                msg = "<b>移除了任务 " + str(uid) + "</b>"
            else:
                if uid == "Empty":
                    msg = "<b>队列为空</b>"
                elif uid == "NotFound":
                    msg = "<b>任务未找到</b>"
            status = bot.sendMessage(chat_id, text=msg,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + "del uid)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text[:len(prefix + "find")] == prefix + "find":
        if len(text.split(" ")) == 2:
            msg = ""
            uid = str(text.split(" ")[1])
            ok, uid = bot.schedule.find(uid)
            if ok:
                msg = "<b>任务存在于队列中</b>"
            else:
                if uid == "Empty":
                    msg = "<b>队列为空</b>"
                elif uid == "NotFound":
                    msg = "<b>任务未找到</b>"
            status = bot.sendMessage(chat_id, text=msg,
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])
        else:
            status = bot.sendMessage(chat_id,
                text="<b>指令格式错误 (e.g.: " + prefix + "del uid)</b>",
                parse_mode="HTML", reply_to_message_id=message_id)
            bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text[:len(prefix + "clear")] == prefix + "clear":
        msg = ""
        ok, msgg = bot.schedule.clear()
        if ok:
            msg = "<b>已清空队列</b>"
        else:
            if msgg == "Empty":
                msg = "<b>队列为空</b>"
            elif msgg != "Cleared":
                msg = "<b>遇到错误</b> \n\n <i>" + msgg + "</i>"

        status = bot.sendMessage(chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])

    elif text[:len(prefix + "status")] == prefix + "status":
        msg = ""
        ok, result = bot.schedule.status()
        if ok:
            msg = "<code>使用: " + str(result["used"]) + "\n" + \
                "空闲: " + str(result["free"]) + "\n" + \
                "容量: " + str(result["size"]) + "</code>\n"
        else:
            msg = "<b>遇到错误</b> \n\n <i>" + result["exception"] + "</i>"
        status = bot.sendMessage(chat_id, text=msg,
            parse_mode="HTML", reply_to_message_id=message_id)
        bot.message_deletor(30, status["chat"]["id"], status["message_id"])



def event(bot, chat_id, msg, parse_mode):
    status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

