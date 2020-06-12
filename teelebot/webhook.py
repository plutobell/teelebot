# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-12
@last modify: 2020-6-12
'''
from flask import Flask
from flask import request

from .teelebot import Bot
from .handler import config

webhook_app = Flask(__name__)
bot = Bot()
config = config()

import logging #隐藏控制台请求日志
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@webhook_app.route("/bot" + str(config["key"]), methods=['POST'])
def index():
    if request.method == 'POST':
        message = request.json
        results = []
        results.append(message)
        messages = bot.washUpdates(results)
        for message in messages:
            bot.pluginRun(message)

        return "ok"

if __name__ == '__main__':
    app.debug=True
    app.run(host="127.0.0.1", port=5000)
