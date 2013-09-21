""" websocket server """
from tornado import websocket, web, ioloop

cl = []

class SocketHandler(websocket.WebSocketHandler):

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)


if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
