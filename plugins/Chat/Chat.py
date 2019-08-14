import sys,requests
sys.path.append("../")
from TeeleBot import teelebot

def Chat(fromm, chat, date, text):
    url1 = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="
    url = "https://api.ownthink.com/bot?spoken="
    requests.adapters.DEFAULT_RETRIES = 5
    status = True
    while(status):
        req = requests.get(url + text[1:])
        req.keep_alive = False
        req.encoding = "utf-8"
        if req.json().get("message") == "success":
            status = False

    bot = teelebot.Bot()
    status = bot.sendMessage(chat["id"], str(req.json().get("data").get("info")["text"]), "text")