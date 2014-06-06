# -*- encoding: utf-8 -*-
""" websocket server """
import json
from tornado import websocket, web, ioloop

from werewolf.models import *
from message_handler import MessageHandler, Message

clients = {}

class SocketHandler(websocket.WebSocketHandler):

    user = None
    village_id = None

    def open(self):
        token = self.get_argument('access_token')
        self.village_id = self.get_argument('village_id')
        if not token or not self.village_id:
            self.write_message(json.dumps(Message(u"認証に失敗しました").to_dict()))
            self.close()
            return
        try:
            self.user = AccessToken.objects.get(token=token).client_session.user
        except AccessToken.DoesNotExist:
            self.write_message(json.dumps(Message(u"認証に失敗しました").to_dict()))
            self.close()
            return
        village_clients = clients.setdefault(self.village_id, [])
        if self not in village_clients:
            clients[self.village_id].append(self)

    def on_message(self, message):
        msg_list = MessageHandler.dispatch(self.village_id, self.user, message)
        if not isinstance(msg_list, list):
            msg_list = [msg_list]
        for msg in msg_list:
            for client in clients[self.village_id]:
                if msg.is_target_user(client.user):
                    client.write_message(json.dumps(msg.to_dict()))

    def on_close(self):
        if self in clients[self.village_id]:
            clients[self.village_id].remove(self)


if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
