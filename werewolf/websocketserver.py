""" websocket server """
from tornado import websocket, web, ioloop
from flask import jsonify

from werewolf.models import *

clients = {}

class SocketHandler(websocket.WebSocketHandler):

    user = None
    village_id = None

    def open(self):
        token = self.get_argument('access_token')
        self.village_id = self.get_argument('village_id')
        self.user = AccessToken.objects.get(token=token).client_session.user
        village_clients = clients.setdefault(self.village_id, [])
        if self not in village_clients:
            clients[self.village_id].append(self)

    def on_message(self, message):
        for client in clients[self.village_id]:
            client.write_message(self.user.name + u": " + message)

    def on_close(self):
        if self in clients[self.village_id]:
            clients[self.village_id].remove(self)


if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
