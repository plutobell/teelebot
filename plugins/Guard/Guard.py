# -*- coding:utf-8 -*-
'''
creation time: 2020-5-28
last_modify: 2020-6-21
'''

from teelebot import Bot
from collections import defaultdict
import re
import string
import sqlite3
import time
from random import shuffle, randint
from threading import Timer
from teelebot.handler import config
from captcha.image import ImageCaptcha
from random import randint
from io import BytesIO

config = config()
bot = Bot()

restrict_permissions = {
    'can_send_messages':False,
    'can_send_media_messages':False,
    'can_send_polls':False,
    'can_send_other_messages':False,
    'can_add_web_page_previews':False,
    'can_change_info':False,
    'can_invite_users':False,
    'can_pin_messages':False
}

def Guard(message):
    repl = "<*>"
    DFA = DFAFilter()
    DFA.parse(bot.plugin_dir + "Guard/keywords")
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    db = SqliteDB()
    gap = 60
    bot_id = bot.key.split(':')[0]

    with open(bot.plugin_dir + "Guard/config.ini") as f:
        data_group_id = f.read().strip()

    result = db.select(chat_id=chat_id, user_id=user_id)
    if "reply_markup" in message.keys() and message["chat"]["type"] != "private":
        user = message["click_user"]
        user_id = user["id"] #未处理：多用户同时点击的情况
        result = db.select(chat_id=chat_id, user_id=user_id)

        if "first_name" in user.keys(): #Optional (first_name or last_name)
            first_name = user["first_name"].strip()
        else:
            first_name = ""
        if "last_name" in user.keys():
            last_name = user["last_name"].strip()
        else:
            last_name = ""

        if result != False and message["callback_query_data"] == "/guardupdatingcaptcha" and result[2] == str(user_id) and result[1] == str(chat_id):
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b> 验证码已手动刷新，请在 <b>"+ str((gap + result[5])-int(time.time())) +"</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text)
            status = bot.sendPhoto(chat_id=str(data_group_id), photo=bytes_image, parse_mode="HTML")
            db.update(message_id=result[3], authcode=captcha_text, chat_id=chat_id, user_id=user_id)
            media = {
                'media':{
                    'type': 'photo',
                    'media': status["photo"][0]["file_id"],
                    'caption': msg,
                    'parse_mode': 'HTML'
                }
            }
            status = bot.editMessageMedia(chat_id=chat_id, message_id=result[3], media=media, reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="刷新成功", show_alert=bool("true"))
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="刷新失败", show_alert=bool("true"))
        elif result != False and message["callback_query_data"] == "/guardcaptchatrue" and result[2] == str(user_id) and result[1] == str(chat_id):
            status = bot.answerCallbackQuery(message["callback_query_id"], text="正确", show_alert=bool("true"))
            status = bot.getChat(chat_id=chat_id)
            chat_title = status["title"]
            permissions = status.get("permissions")
            status = bot.restrictChatMember(chat_id=chat_id, user_id=result[2], permissions=permissions)
            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b>, 欢迎加入 <b>" + str(chat_title) + "</b>。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

            timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
            timer.start()

        elif result != False and "/guardcaptchafalse" in message["callback_query_data"] and result[2] == str(user_id) and result[1] == str(chat_id):
            status = bot.answerCallbackQuery(message["callback_query_id"], text="不正确", show_alert=bool("true"))
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b> 验证码不正确，已刷新，请在 <b>"+ str((gap + result[5])-int(time.time())) +"</b> 秒内从下方选出与图片一致的验证码。"
            bytes_image, captcha_text = captcha_img()
            reply_markup = reply_markup_dict(captcha_text=captcha_text)
            status = bot.sendPhoto(chat_id=str(data_group_id), photo=bytes_image, parse_mode="HTML")
            db.update(message_id=result[3], authcode=captcha_text, chat_id=chat_id, user_id=user_id)
            media = {
                'media':{
                        'type': 'photo',
                        'media': status["photo"][0]["file_id"],
                        'caption': msg,
                        'parse_mode': 'HTML'
                }
            }
            status = bot.editMessageMedia(chat_id=chat_id, message_id=result[3], media=media, reply_markup=reply_markup)
            if status != False:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="刷新成功", show_alert=bool("true"))
            else:
                status = bot.answerCallbackQuery(message["callback_query_id"], text="刷新失败", show_alert=bool("true"))
        elif message["callback_query_data"] in "/guardupdatingcaptcha" or "/guardcaptcha" in message["callback_query_data"]: #防止接收来自其他插件的CallbackQuery
            status = bot.answerCallbackQuery(message["callback_query_id"], text="点啥点，关你啥事？", show_alert=bool("true"))

    elif "new_chat_members" in message.keys():
        status = bot.restrictChatMember(chat_id=chat_id, user_id=user_id,permissions=restrict_permissions, until_date=gap+5)

        results = bot.getChatAdministrators(chat_id=chat_id) #判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
            timer.start()
            return False

        new_chat_members = message["new_chat_members"]
        for new_chat_member in new_chat_members:
            if str(bot_id) == str(new_chat_member["id"]):
                continue

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
                status = bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=35)
                status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
                msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a></b> 的名字<b> 违规</b>，已驱逐出境。"
                status = bot.sendChatAction(chat_id, "typing")
                status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

                timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
                timer.start()
            else:
                status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b> 您好，本群已开启人机验证，请在 <b>"+ str(gap) +"</b> 秒内从下方选出与图片一致的验证码。"
                bytes_image, captcha_text = captcha_img()
                reply_markup = reply_markup_dict(captcha_text=captcha_text)
                status = bot.sendPhoto(chat_id=chat_id, photo=bytes_image, caption=msg, parse_mode="HTML", reply_markup=reply_markup)
                db.insert(chat_id=chat_id, user_id=user_id, message_id=status["message_id"], authcode=captcha_text)
                timer = Timer(gap + 1, timer_func, args=[gap, chat_id, user_id, first_name, last_name])
                timer.start()

    elif "left_chat_member" in message.keys():
        results = bot.getChatAdministrators(chat_id=chat_id) #判断Bot是否具管理员权限
        admin_status = False
        for admin_user in results:
            if str(admin_user["user"]["id"]) == str(bot_id):
                admin_status = True
        if admin_status != True:
            status = bot.sendChatAction(chat_id, "typing")
            msg = "权限不足，请授予删除消息及封禁用户权限以使用 Guard 插件。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")
            timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
            timer.start()
            return False

        result = db.select(chat_id=message["chat"]["id"], user_id=message["left_chat_member"]["id"])
        if  result != False and result[2] == str(user_id) and result[1] == str(chat_id) and message["chat"]["type"] != "private":
            status = bot.deleteMessage(chat_id=message["chat"]["id"], message_id=result[3])
            db.delete(chat_id=message["chat"]["id"], user_id=message["left_chat_member"]["id"])

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
            msg = "<b><a href='tg://user?id="+ str(user_id) + "'>"+ first_name + " " + last_name +"</a></b> 离开了我们。"
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

            timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
            timer.start()

    elif "text" in message.keys():
        text = message["text"]
        prefix = "guard"
        gap = 15

        command = {
            "/guardadd": "add"
        }
        count = 0
        for c in command.keys():
            if c in str(text):
                count += 1

        if count > 0 or text[1:len(prefix)+1] == prefix: #在命令列表则删除用户指令
            timer = Timer(gap, timer_func_for_del, args=[chat_id, message_id])
            timer.start()

        if message["chat"]["type"] != "private":
            admins = administrators(chat_id=chat_id)
            if str(config["root"]) not in admins:
                admins.append(str(config["root"])) #root permission

        if message["chat"]["type"] == "private" and text[1:len(prefix)+1] == prefix: #判断是否为私人对话
            status = bot.sendChatAction(chat_id, "typing")
            status = bot.sendMessage(chat_id, "抱歉，该指令不支持私人会话!", parse_mode="text", reply_to_message_id=message_id)
            timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
            timer.start()
        elif text[1:len(prefix)+1] == prefix and count == 0: #菜单
            status = bot.sendChatAction(chat_id, "typing")
            msg = "<b>===== Guard 插件功能 =====</b>%0A%0A" +\
                "<b>/guardadd</b> - 新增过滤关键词，一次只能添加一个。格式：命令后接关键词，以空格作为分隔符%0A" +\
                "%0A"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message["message_id"])

            timer = Timer(30, timer_func_for_del, args=[chat_id, status["message_id"]])
            timer.start()
        elif count > 0:
            if text[1:len(prefix + command["/guardadd"])+1] == prefix + command["/guardadd"]:
                if len(text.split(' ')) == 2:
                    keyword = (text.split(' ')[1]).strip()
                    if str(user_id) in admins and len(keyword) <= 7:
                        result = DFA.filter(keyword, repl)
                        if repl not in result:
                            with open(bot.plugin_dir + "Guard/keywords", "a", encoding="utf-8") as k:
                                k.write("\n" + keyword)
                            status = bot.sendChatAction(chat_id, "typing")
                            status = bot.sendMessage(chat_id=chat_id, text="关键词添加成功!", parse_mode="text", reply_to_message_id=message["message_id"])
                            timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                            timer.start()
                        else:
                            status = bot.sendChatAction(chat_id, "typing")
                            status = bot.sendMessage(chat_id=chat_id, text="关键词已经存在于库中!", parse_mode="text", reply_to_message_id=message["message_id"])
                            timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                            timer.start()
                    elif len(keyword) > 7:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text="输入的关键词过长!", parse_mode="text", reply_to_message_id=message["message_id"])
                        timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                        timer.start()
                    else:
                        status = bot.sendChatAction(chat_id, "typing")
                        status = bot.sendMessage(chat_id=chat_id, text="您无权操作!", parse_mode="text", reply_to_message_id=message["message_id"])
                        timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                        timer.start()
                else:
                    status = bot.sendChatAction(chat_id, "typing")
                    status = bot.sendMessage(chat_id=chat_id, text="操作失败，请检查命令格式!", parse_mode="text", reply_to_message_id=message["message_id"])
                    timer = Timer(gap, timer_func_for_del, args=[chat_id, status["message_id"]])
                    timer.start()


def timer_func_for_del(chat_id, message_id):
    status = bot.deleteMessage(chat_id=chat_id, message_id=message_id)


def timer_func(gap, chat_id, user_id, first_name, last_name):
    db = SqliteDB()
    result = db.select(chat_id=chat_id, user_id=user_id)
    if result != False and result[2] == str(user_id) != "private":
        if int(time.time()) > result[5] + gap:
            status = bot.deleteMessage(chat_id=chat_id, message_id=result[3])
            db.delete(chat_id=chat_id, user_id=user_id)
            status = bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=35)
            #status = bot.unbanChatMember(chat_id=chat_id, user_id=user_id)
            msg = "<b><a href='tg://user?id=" + str(user_id) + "'>" + first_name + " " + last_name + "</a></b> 没能通过人机验证。"
            status = bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="HTML")

            timer = Timer(30, timer_func_for_del, args=[status["chat"]["id"], status["message_id"]])
            timer.start()


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

def shuffle_str(s):
    str_list = list(s)
    shuffle(str_list)

    return ''.join(str_list)

def captcha_img(width=160, height=60, font_sizes=(50, 55, 60), fonts=None):

    captcha_len = 5
    #captcha_range = string.digits + string.ascii_letters #大小写+数字
    captcha_range = string.ascii_lowercase
    captcha_range_len = len(captcha_range)
    captcha_text = ""
    for i in range(captcha_len):
        captcha_text += captcha_range[randint(0, captcha_range_len-1)]

    img = ImageCaptcha(width=width, height=height, font_sizes=font_sizes)
    image = img.generate_image(captcha_text)

    #save to bytes
    bytes_image = BytesIO()
    image.save(bytes_image, format='png')
    bytes_image = bytes_image.getvalue()

    return bytes_image, captcha_text

def reply_markup_dict(captcha_text):
    answer = randint(0,3)
    options = []
    while True:
        for i in range(4): #生成答案列表
            if  answer == i:
                options.append(captcha_text)
            else:
                options.append(shuffle_str(captcha_text))
        if len(options) == len(set(options)):
            break
        else: #存在重复的情况下清空options，防止死循环
            options = []

    callback_data = []
    for i in range(4): #生成callback_data列表
        if answer == i:
            callback_data.append("/guardcaptchatrue")
        else:
            callback_data.append("/guardcaptchafalse" + str(i))

    inlineKeyboard = [
        [
            {"text": options[0],"callback_data":callback_data[0]},
            {"text": options[1],"callback_data":callback_data[1]},
        ],
        [
            {"text": options[2],"callback_data":callback_data[2]},
            {"text": options[3],"callback_data":callback_data[3]},
        ],
        [
            {"text": "看不清，换一张","callback_data":"/guardupdatingcaptcha"},
        ]
    ]
    reply_markup = {
        "inline_keyboard": inlineKeyboard
    }
    #print(inlineKeyboard)

    return reply_markup

class SqliteDB(object):
    def __init__(self):
        '''
        Open the connection
        '''
        self.conn = sqlite3.connect(bot.plugin_dir + "Guard/captcha.db", check_same_thread=False) #只读模式加上uri=True
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS captcha_list (id INTEGER PRIMARY KEY autoincrement, chat_id TEXT, user_id TEXT, message_id TEXT, authcode TEXT, timestamp INTEGER)")

    def __del__(self):
        '''
        Close the connection
        '''
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def insert(self, chat_id, user_id, message_id, authcode):
        '''
        Insert
        '''
        timestamp = int(time.time())
        self.cursor.execute("INSERT INTO captcha_list (chat_id, user_id, message_id, authcode, timestamp) VALUES (?,?,?,?,?)", (chat_id, user_id, message_id, authcode, timestamp))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def select(self, chat_id, user_id):
        '''
        Select
        '''
        self.cursor.execute("SELECT * FROM captcha_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        result = self.cursor.fetchall()

        if result:
            result = result[0]
        else:
            result = False

        return result


    def delete(self, chat_id, user_id):
        '''
        Delete
        '''
        self.cursor.execute("DELETE FROM captcha_list WHERE chat_id=? AND user_id=?", (chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

    def update(self, message_id, authcode, chat_id, user_id, timestamp=None):
        '''
        Update
        '''
        if timestamp == None:
            self.cursor.execute("UPDATE captcha_list SET message_id=?, authcode=? WHERE chat_id=? and user_id=?", (message_id, authcode, chat_id, user_id))
        else:
            self.cursor.execute("UPDATE captcha_list SET message_id=?, authcode=?, timestamp=? WHERE chat_id=? and user_id=?", (message_id, authcode, int(timestamp), chat_id, user_id))

        if self.cursor.rowcount == 1:
            return True
        else:
            return False

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