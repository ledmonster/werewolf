""" websocket server """
from tornado import websocket, web, ioloop

from werewolf.models import *

clients = []

class SocketHandler(websocket.WebSocketHandler):

    user = None

    def open(self):
        token = self.get_argument('access_token')
        self.user = AccessToken.objects.get(token=token).client_session.user
        if self not in clients:
            clients.append(self)

    def on_message(self, message):
        for client in clients:
            client.write_message(self.user.name + u" said: " + message)

    def on_close(self):
        if self in clients:
            clients.remove(self)


if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
