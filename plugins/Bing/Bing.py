# -*- coding:utf-8 -*-
import requests, lxml, os, time
from teelebot import Bot
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用HTTPS安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def Bing(message):
    '''
    Bing接口Github地址:https://github.com/xCss/bing
    '''

    bot = Bot()
    headers = {
        'Host': 'bing.ioliu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'
    }
    url = "https://bing.ioliu.cn"
    req = requests.post(url, headers=headers, verify=False)
    soup = BeautifulSoup(req.text,"lxml")
    item = soup.find_all("div", class_="item")[0]
    desc = item.find("h3").text
    date = item.find("em").text
    src = url + item.find("a", class_="ctrl download")["href"]
    if not os.path.isfile(bot.plugin_dir + "Bing/status.db"):
        with open(bot.plugin_dir + "Bing/status.db", "w") as f:
            f.write(str(time.strftime('%Y-%m-%d')))
    if not os.path.isfile(bot.plugin_dir + "Bing/today.jpg"):
        with open(bot.plugin_dir + "Bing/today.jpg", "wb") as p:
            req = requests.get(src, headers=headers)
            p.write(req.content)

    with open(bot.plugin_dir + "Bing/status.db", "r") as f:
        old = f.readline().strip()
    if date != old:
        req = requests.get(src, headers=headers)
        with open(bot.plugin_dir + "Bing/today.jpg", "wb") as p:
            p.write(req.content)
        with open(bot.plugin_dir + "Bing/status.db", "w") as f:
            f.write(str(date))

    status = bot.sendChatAction(message["chat"]["id"], "typing")
    status = bot.sendPhoto(chat_id=message["chat"]["id"], photo=bot.plugin_dir + "Bing/today.jpg", caption=desc+"%0A%0A"+date, parse_mode="HTML", reply_to_message_id=message["message_id"])