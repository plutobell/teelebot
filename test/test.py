# -*- coding:utf-8 -*-
import sys
sys.path.append("..")

import teelebot

bot = teelebot.Bot()
root = bot.root_id

# print(bot.logOut())
# print(bot.close())
# print(bot.getWebhookInfo())



#bot.sendMessage(chat_id=chat_id, text="测试消息", parse_mode="text")

# bot.restrictChatMember(chat_id=chat_id, user_id=user_id, can_change_info=False, can_post_messages=False, \
#                         can_edit_messages=False, can_delete_messages=False, can_invite_users=False, \
#                         can_restrict_members=False, can_pin_messages=False, can_promote_members=False)

#bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=3600)

#bot.unbanChatMember(chat_id=chat_id, user_id=user_id)

medias ={
    'caption': 'test',
    'media': [
        {
            'type': 'photo',
            'media': 'http://pic1.win4000.com/pic/d/6a/25a2c0e959.jpg'
        },
        {
            'type': 'photo',
            'media': 'http://pic1.win4000.com/pic/d/6a/7c6a73b5bd.jpg'
        },
        {
            'type': 'photo',
            'media': 'AgACAgQAAx0ETbyLwwADeF5s6QosSI_IW3rKir3PrMUXdMFMAALeqjEbhENsU84zcAUOKKcVdpWgGwAEAQADAgADeAADwKIIAAEYBA'
        }
    ]
}
#req = bot.sendMediaGroup(chat_id=chat_id, medias=medias)
#print(req)


#r = bot.deleteMessage(chat_id=chat_id, message_id=190)
#print(r)


#r = bot.editMessageText(chat_id=chat_id, message_id=198, text="测试修改消息")
#print(r)
results = {
    '1':'a',
    '2':'b',
    '3':'c'
}
# r = bot.answerInlineQuery(inline_query_id="4193969412829691548", results=results)
# print(r)


# replyKeyboard = [
#   [
#     {  "text": "/start"},
#     {  "text": "/bing"}
#   ],
#   [
#     { "text": "/id"},
#     { "text": "/top"},
#     { "text": "/helloword"}
#   ]
# ]
# reply_markup = {
#     "keyboard": replyKeyboard,
#     "resize_keyboard": bool("true"),
#     "one_time_keyboard": bool("true"),
#     "selective": bool("false")
# }
# r = bot.sendMessage(chat_id=user_id, text="测试keyboard", reply_markup=reply_markup)
# print(r)
# r = bot.unbanChatMember(chat_id=chat_id, user_id=)
# print(r)



# admins = [] #获取群组所有管理员id
# results = bot.getChatAdministrators(chat_id=chat_id)
# for result in results:
#     if str(result["user"]["is_bot"]) == "False":
#         admins.append(result["user"]["id"])
# print(admins)


#import cap
# bytes_captcha, captcha_text = cap.captcha_img()
# r = bot.sendPhoto(chat_id=chat_id, photo=bytes_captcha, caption="测试验证码图片发送", parse_mode="Text")
# print(r)



# req = bot.sendMessage(chat_id=chat_id, text="被编辑的消息", parse_mode="HTML")
# print(req)
# import time
# time.sleep(2)
# req = bot.editMessageText(text="编辑后的消息", chat_id=chat_id, message_id=req["message_id"])
# print(req)


# import cap
# bytes_captcha, captcha_text = cap.captcha_img()
# req = bot.sendPhoto(chat_id=chat_id, photo=bytes_captcha, caption="测试编辑caption", parse_mode="Text")
# print(req)
# import time
# time.sleep(2)
# req = bot.editMessageCaption(chat_id=chat_id, caption="编辑后的caption", message_id=req["message_id"])
# print(req)


# import cap  #//TODO
# bytes_captcha, captcha_text = cap.captcha_img()
# req = bot.sendPhoto(chat_id=user_id, photo=bytes_captcha, caption="测试编辑Media", parse_mode="Text")
# print(req)
# import time
# time.sleep(2)
# bytes_captcha, captcha_text = cap.captcha_img()
# media = {
#     'media':{
#             'type': 'photo',
#             'media': 'http://pic1.win4000.com/pic/d/6a/25a2c0e959.jpg',
#             'caption': '编辑后的Media'
#     }
# }
# req = bot.editMessageMedia(chat_id=user_id, message_id=req["message_id"], media=media)
# print(req)

# req = bot.deleteMessage(chat_id=chat_id,message_id=104656)
# print(req)

# permissions = {
#             'can_send_messages':False,
#             'can_send_media_messages':False,
#             'can_send_polls':False,
#             'can_send_other_messages':False,
#             'can_add_web_page_previews':False,
#             'can_change_info':False,
#             'can_invite_users':False,
#             'can_pin_messages':False
#         }
# req = bot.restrictChatMember(chat_id=chat_id, user_id=config["root"], permissions=permissions, until_date=60)
# print(req)


# req = bot.getChat(chat_id=chat_id)
# print(req.get("permissions"), len(req.get("permissions")))
# status = bot.restrictChatMember(chat_id=chat_id, user_id=config["root"], permissions=req.get("permissions"))
# print(status)

# bot_id = str(bot.getMe()["id"])
# req = bot.getUserProfilePhotos(user_id=bot_id, limit=1)
# print(req.get("photos")[0][0]["file_id"])

# req = bot.getFileDownloadPath(file_id="AAMCBQADGQEAAgnHXuCO-vFvdz4zDftTyEdVXkLLdVgAAvYAA7UTei_hUL93SWi3DkVAmmp0AAMBAAdtAANcOAACGgQ")
# print(req)

# req = bot.getWebhookInfo()
# print(req)
# req = bot.deleteWebhook()
# print(req)
# status = bot.setWebhook("https://telegram_bot.123.com")
# req = bot.deleteWebhook()
# print(req)
# req = bot.getWebhookInfo()
# print(req)

# bot.sendPhoto("123456789", "123456789")

# print(bot.uptime(time_format="format"))



# commands = [
#     {"command": "start", "description": "插件列表"}
# ]
# req = bot.setMyCommands(commands)
# print(req)

# req = bot.getMyCommands()
# print(req)


# req = bot.sendLocation(chat_id=config["root"],
#         latitude="38.913611", longitude="77.013222",
#         live_period=600)
# print(req)
# req = bot.editMessageLiveLocation(chat_id=config["root"], message_id=req["message_id"],
#         latitude="39.913611", longitude="78.013222")
# print(req)
# req = bot.stopMessageLiveLocation(chat_id=config["root"], message_id=req["message_id"])
# print(req)


# req1 = bot.getChat(chat_id="")
# print(req1["permissions"])
# permissions = {
#     'can_send_messages':False,
#     'can_send_media_messages':False,
#     'can_send_polls':False,
#     'can_send_other_messages':False,
#     'can_add_web_page_previews':False,
#     'can_change_info':False,
#     'can_invite_users':False,
#     'can_pin_messages':False
# }
# req = bot.setChatPermissions(chat_id="", permissions=permissions)
# print(req)
# import time
# time.sleep(10)
# req = bot.setChatPermissions(chat_id="", permissions=req1["permissions"])
# print(req)


# req = bot.sendSticker(chat_id=config["root"], sticker="http://wx4.sinaimg.cn/mw690/6a04b428gy1g0gvw312lxg202z02bt8k.gif")
# print(req)
# req = bot.getStickerSet(name="Umaru")
# print(req)


# from random import randint
# bot.sendSticker(chat_id=config["root"], sticker=bot.plugin_dir + "Uptime/umaru/" + str(randint(1,3)) + ".gif")


# status = bot.createChatInviteLink(chat_id="chat_id",
#     expire_date=600, member_limit=10)
# print(status)

# status = bot.editChatInviteLink(chat_id="chat_id",
#     invite_link="invite_link", expire_date=100, member_limit=100)
# print(status)

# status = bot.revokeChatInviteLink(chat_id="chat_id",
#     invite_link="invite_link")
# print(status)


# status = bot.kickChatMember(chat_id="chat_id", user_id="user_id",
#     until_date=60, revoke_messages=True)
# print(status)



# permissions = {
#     'is_anonymous':False,
#     'can_manage_chat':True,
#     'can_change_info':False,
#     'can_post_messages':False,
#     'can_edit_messages':False,
#     'can_delete_messages':False,
#     'can_manage_voice_chats':False,
#     'can_invite_users':False,
#     'can_restrict_members':False,
#     'can_pin_messages':False,
#     'can_promote_members':False
# }
# ok = bot.promoteChatMember(
#     chat_id = "chat_id",
#     user_id = "user_id",
#     is_anonymous = False,
#     can_manage_chat=True,
#     can_change_info = False,
#     can_post_messages = False,
#     can_edit_messages = False,
#     can_delete_messages = False,
#     can_invite_users = False,
#     can_restrict_members = False,
#     can_pin_messages = False,
#     can_promote_members = False
# )
# print(ok)



# status = bot.sendDice(chat_id="chat_id", emoji="🎳")
# print(status)



# with open('test.jpg', 'rb') as f:
#     fbytes = f.read()
# status = bot.editMessageMedia(chat_id=bot.root_id,
#     message_id="id", type_="photo", media=fbytes,
#     caption="测试修改<b>test</b>", parse_mode="HTML")
# print(status)


# commands = [
#     {"command": "start", "description": "插件列表"},
#     {"command": "test", "description": "测试API5.3"}
# ]
# scope = {"type": "all_chat_administrators"}

# req = bot.setMyCommands(commands, scope, "zh")
# print(req)

# commands = [
#     {"command": "testen", "description": "插件列表en"}
# ]
# req = bot.setMyCommands(commands, language_code="en")
# print(req)
# req = bot.getMyCommands(language_code="en")
# print(req)

# req = bot.deleteMyCommands(language_code="en")
# print(req)
# req = bot.getMyCommands()
# print(req)


# req = bot.createChatInviteLink(chat_id="chat_id",
#     creates_join_request=True, name="test")
# print(req)
# req = bot.editChatInviteLink(chat_id="chat_id",
#     invite_link=req["invite_link"],
#     name="test1", creates_join_request=False)
# print(req)
# req = bot.revokeChatInviteLink(chat_id="chat_id",
#     invite_link=req["invite_link"])
# print(req)

# menu_button = {
#     "type": "web_app",
#     "text": "button text",
#     "web_app": {
#         "url": "https://google.com"
#     }
# }
# req = bot.setChatMenuButton(chat_id="chat_id", menu_button=menu_button)
# print(req)
# req = bot.getChatMenuButton()
# print(req)

# rights = {
#     "is_anonymous": False,
#     "can_manage_chat": True,
#     "can_delete_messages": True,
#     "can_manage_video_chats": True,
#     "can_restrict_members": True,
#     "can_promote_members": True,
#     "can_change_info": False,
#     "can_invite_users": True,
#     "can_post_messages": True,
#     "can_edit_messages": True,
#     "can_pin_messages": True
# }
# req = bot.setMyDefaultAdministratorRights(rights=rights, for_channels=True)
# print(req)
# req = bot.getMyDefaultAdministratorRights(for_channels=True)
# print(req)