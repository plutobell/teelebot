# -*- coding:utf-8 -*-
'''
@creation date: 2020-6-12
@last modify: 2020-6-23
'''
from http.server import HTTPServer, BaseHTTPRequestHandler
#from socketserver import ThreadingMixIn
import json
import sys

def __MakeRequestHandler(bot):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
                super(RequestHandler, self).__init__(*args, **kwargs)

        def do_POST(self):
            if self.command == "POST" and self.path == "/bot" + str(bot.key):
                req_data = self.rfile.read(int(self.headers['content-length']))
                res = req_data.decode('utf-8')

                data = {'status':'ok'}
                data = json.dumps(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))

                message = json.loads(res)
                results = []
                results.append(message)
                messages = bot._washUpdates(results)
                if messages != None and messages != False:
                    for message in messages:
                        bot._pluginRun(bot, message)
            else:
                data = {'status':'false'}
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


def runWebhook(bot, host, port):
    RequestHandler = __MakeRequestHandler(bot)
    server = HTTPServer((host, port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        sys.exit("程序终止")


if __name__ == '__main__':
    try:
        runWebhook()
    except KeyboardInterrupt:
        sys.exit("exit")