# -*- coding:utf-8 -*-
import sys
sys.path.append("..")

import teelebot
from teelebot.handler import config

config = config()
bot = teelebot.Bot()
user_id = config['root']

bot.sendMessage(chat_id=chat_id, text="测试消息", parse_mode="text")

bot.restrictChatMember(chat_id=chat_id, user_id=user_id, can_change_info=False, can_post_messages=False, \
                        can_edit_messages=False, can_delete_messages=False, can_invite_users=False, \
                        can_restrict_members=False, can_pin_messages=False, can_promote_members=False)

bot.kickChatMember(chat_id=chat_id, user_id=user_id, until_date=3600)

bot.unbanChatMember(chat_id=chat_id, user_id=user_id)

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
req = bot.sendMediaGroup(chat_id=chat_id, medias=medias)
print(req)