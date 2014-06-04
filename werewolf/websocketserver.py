""" websocket server """
import json
from tornado import websocket, web, ioloop

from werewolf.models import *
from message_handler import MessageHandler

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
        res_msg = MessageHandler.dispatch(self.village_id, self.user, message)
        for client in clients[self.village_id]:
            if res_msg.is_target_user(client.user.identity):
                client.write_message(json.dumps(res_msg.to_dict()))

    def on_close(self):
        if self in clients[self.village_id]:
            clients[self.village_id].remove(self)


if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
