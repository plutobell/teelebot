# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-12
@last modification: 2023-11-28
'''
#from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os
import json

from .logger import _logger


def __MakeRequestHandler(bot):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super(RequestHandler, self).__init__(*args, **kwargs)

        def do_POST(self):
            if self.command == "POST" and \
            self.path == "/bot" + str(bot._key) and \
            str(self.headers['X-Telegram-Bot-Api-Secret-Token']) == bot._secret_token:
                req_data = self.rfile.read(int(self.headers['content-length']))
                res = req_data.decode('utf-8')

                message = json.loads(res)
                results = [message]
                messages = bot._washUpdates(results)
                if messages is not None and messages:
                    for message in messages:
                        bot._pluginRun(bot, message)

                data = {'status': 'ok'}
                data = json.dumps(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            else:
                data = {'status': 'false'}
                data = json.dumps(data)
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))

        def log_message(self, format, *args):
            pass

    return RequestHandler


# class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#     pass


def _runWebhook(bot, host, port):
    _logger.info("Bot Start.")

    RequestHandler = __MakeRequestHandler(bot)
    if bot._load_cert:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(bot._cert_pub, bot._cert_key)

            server = HTTPServer((host, port), RequestHandler)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            _logger.info("Bot Exit.")
            os._exit(0)
    else:
        try:
            server = HTTPServer((host, port), RequestHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            _logger.info("Bot Exit.")
            os._exit(0)
