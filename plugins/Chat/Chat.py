import sys,requests
sys.path.append("../")
from TeeleBot import teelebot
import urllib.parse as ubp

def Chat(message):
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg="
    url1 = "https://api.ownthink.com/bot?spoken="
    requests.adapters.DEFAULT_RETRIES = 5
    req = requests.get(url + ubp.quote(message["text"][1:])) #urlencode编码
    req.keep_alive = False
    req.encoding = "utf-8"
    bot = teelebot.Bot()
    status = bot.sendMessage(message["chat"]["id"], str(req.json().get("content").replace("{br}", "%0A")), "html")