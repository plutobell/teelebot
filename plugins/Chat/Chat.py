import sys,requests
sys.path.append("../")
from TeeleBot import teelebot

def Chat(fromm, chat, date, text):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="
    url1 = "https://api.ownthink.com/bot?spoken="
    requests.adapters.DEFAULT_RETRIES = 5
    req = requests.get(url + text[1:])
    req.keep_alive = False
    req.encoding = "utf-8"

    bot = teelebot.Bot()
    status = bot.sendMessage(chat["id"], str(req.json().get("content").replace("{br}", "%0A")), "html")