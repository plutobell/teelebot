# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-12
@last modify: 2020-11-23
'''
from http.server import HTTPServer, BaseHTTPRequestHandler
#from socketserver import ThreadingMixIn
import ssl
import sys
import json


def __MakeRequestHandler(bot):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super(RequestHandler, self).__init__(*args, **kwargs)

        def do_POST(self):
            if self.command == "POST" and self.path == "/bot" + str(bot._key):
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
    RequestHandler = __MakeRequestHandler(bot)
    if bot._local_address == "0.0.0.0":
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(bot._cert_pub, bot._cert_key)

            server = HTTPServer((host, port), RequestHandler)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            sys.exit("Bot Exit.")
    else:
        try:
            server = HTTPServer((host, port), RequestHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            sys.exit("Bot Exit.")
