# -*- coding: utf-8 -*-
""" websocket server """
import json
from tornado import websocket, web, ioloop

from werewolf.domain.game.models import *
from werewolf.domain.user.models import *
from werewolf.app.message_handler import MessageHandler

clients = {}

class SocketHandler(websocket.WebSocketHandler):

    user = None
    village_id = None

    def open(self):
        token = self.get_argument('access_token')
        self.village_id = self.get_argument('village_id')
        if not token or not self.village_id:
            msg = MessageHandler.get_auth_error_message()
            self.write_message(json.dumps(msg.to_dict()))
            self.close()
            return
        try:
            self.user = AccessToken.objects.get(token=token).client_session.user
        except AccessToken.DoesNotExist:
            msg = MessageHandler.get_auth_error_message()
            self.write_message(json.dumps(msg.to_dict()))
            self.close()
            return
        village_clients = clients.setdefault(self.village_id, [])
        if self not in village_clients:
            clients[self.village_id].append(self)

        # send initial messages
        msg_list = MessageHandler.get_initial_messages(self.village_id, self.user)
        for msg in msg_list:
            if msg.is_target_user(self.user):
                self.write_message(json.dumps(msg.to_dict()))

        # send coming message
        for client in clients[self.village_id]:
            msg = MessageHandler.get_coming_message(self.user)
            client.write_message(json.dumps(msg.to_dict()))

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

        # send leaving message
        for client in clients[self.village_id]:
            msg = MessageHandler.get_leaving_message(self.user)
            client.write_message(json.dumps(msg.to_dict()))

if __name__ == '__main__':
    app = web.Application([
        (r'/websocket', SocketHandler),
    ])
    app.listen(8888)
    ioloop.IOLoop.instance().start()
