# -*- coding:utf-8 -*-
import sys, requests, lxml, os, time
sys.path.append("../")
from teelebot import Bot
from bs4 import BeautifulSoup

def Bing(message):
    '''
    Bing接口Github地址:https://github.com/xCss/bing
    '''

    bot = Bot()

    url = "https://bing.ioliu.cn"
    req = requests.get(url)
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
            req = requests.get(src)
            p.write(req.content)

    with open(bot.plugin_dir + "Bing/status.db", "r") as f:
        old = f.readline().strip()
    if date != old:
        req = requests.get(src)
        with open(bot.plugin_dir + "Bing/today.jpg", "wb") as p:
            p.write(req.content)
        with open(bot.plugin_dir + "Bing/status.db", "w") as f:
            f.write(str(date))

    status = bot.sendPhoto(chat_id=message["chat"]["id"], photo=bot.plugin_dir + "Bing/today.jpg", caption=desc+"%0A%0A"+date, parse_mode="html")