import sys
sys.path.append("../")
from TeeleBot import teelebot
import requests, lxml, hashlib
from bs4 import BeautifulSoup

def Firefoxmoniter(message):
    with open("plugins/Firefoxmoniter/__init__.py", encoding="utf-8") as f:
        h = f.readline()[1:]
    if len(message["text"]) < len(h):
        bot = teelebot.Bot()
        status = bot.sendMessage(message["chat"]["id"], "查询失败！%0A邮件地址为空!", "html")
        return False
    email = message["text"][len(h)-1:]
    if all([ '@' in email, '.' in email.split('@')[1] ]):
        ehash = hashlib.sha1(email.encode("utf-8")) #经测试由sha1加密
        emailhash = ehash.hexdigest()
    else:
        bot = teelebot.Bot()
        status = bot.sendMessage(message["chat"]["id"], "查询失败！%0A请检查邮件格式!", "html")
        return False

    url = "https://monitor.firefox.com/"
    r_session = requests.Session()
    page = r_session.get(url)
    page.encoding = "utf-8"
    soup = BeautifulSoup(page.text, "lxml")

    session = page.cookies["session"]
    csrf = soup.find_all("input")[0]["value"]

    url = "https://monitor.firefox.com/scan"
    data = {
        '_csrf': csrf,
        'email': email,
        'emailHash': emailhash
    }
    headers = {
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'session=' + session + "; _ga=GA1.3.1750251620.1566005038; _gid=GA1.3.1329192982.1566005038; _gat=1;",
        'origin': 'https://monitor.firefox.com',
        'referer': 'https://monitor.firefox.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    page = r_session.post(url, data=data, headers=headers)
    page.encoding = "utf-8"

    result = ""
    soup = BeautifulSoup(page.text, "lxml")
    if "扫描结果" in soup.find("title").text:
        result += "电子邮件地址" + email +"出现在" + str(soup.find("span", class_="bold").text) + "次已知数据外泄事件中。%0A%0A"
        for section in soup.find_all("div", class_="flx flx-col"):
            source = section.find_all("span")[0].text + "%0A"
            date = "事件记录时间:%0A" + section.find_all("span")[2].text + "%0A"
            data = "泄露的数据:%0A" + section.find_all("span")[4].text + "%0A"
            result += source + date + data + "%0A%0A"

        bot = teelebot.Bot()
        status = bot.sendMessage(message["chat"]["id"], result, "html")
    else:
        bot = teelebot.Bot()
        status = bot.sendMessage(message["chat"]["id"], "查询失败！%0A请检测命令格式!", "text")


if __name__ == "__main__":
    Firefoxmoniter("hi@ojoll.com")