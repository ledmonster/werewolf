# -*- coding: utf-8 -*-
import logging
from functools import update_wrapper

from pyramid.response import Response
from pyramid.view import view_config
from socketio.namespace import BaseNamespace
from socketio import socketio_manage

from werewolf.domain.game.models import *
from werewolf.domain.user.models import *


logger = logging.getLogger(__name__)


def auth_required(func):
    u""" user が設定されていない場合に error を返す """
    def wrapper_func(self, *args, **kwargs):
        if self.session.get('user') is None:
            self.error('authentication required', u'認証してください')
            self.disconnect()
            return
        return func(self, *args, **kwargs)
    return update_wrapper(wrapper_func, func)


class ChatNamespace(BaseNamespace):
    u""" チャット空間

    Note:

    - room には village_id を使うが、村(village)と部屋(room)は異なるので注意。
      村に参加していなくても部屋に入ってメッセージを送受信することはできる。

    """

    def __init__(self, *args, **kwargs):
        super(ChatNamespace, self).__init__(*args, **kwargs)
        if 'room_list' not in self.session:
            self.session['room_list'] = set()

    def initialize(self):
        self.log("Socketio session started")
        self.message_handler = self.request.context.message_handler

    def log(self, message):
        logger.info("[{0}] {1}".format(self.socket.sessid, message))

    @auth_required
    def on_join(self, village_id):
        u""" 部屋に参加する """
        room_name = self._get_room_name(village_id)
        self.session['room_list'].add(room_name)
        self.village_id = village_id

        # send initial messages
        msg_list = self.message_handler.get_initial_messages(village_id, self.session.get("user"))
        room_name = self._get_room_name(village_id)
        self._send_messages(room_name, msg_list)

        # send coming message
        msg_list = [self.message_handler.get_coming_message(self.session.get("user"))]
        self._send_messages(room_name, msg_list)

        return True

    @auth_required
    def on_leave(self, village_id):
        u""" 部屋を離れる """
        room_name = self._get_room_name(village_id)
        self.session['room_list'].remove(room_name)
        self.village_id = None

        return True

    def _get_room_name(self, village_id):
        u""" 部屋の名前を返す。デフォルトは village_id そのもの """
        return village_id

    @auth_required
    def on_message(self, message):
        u"""" クライアントから受信したメッセージを処理 (event == 'message') """
        msg_list = self.message_handler.dispatch(self.village_id, self.session.get('user'), message)
        if not isinstance(msg_list, list):
            msg_list = [msg_list]

        room_name = self._get_room_name(self.village_id)
        self._send_messages(room_name, msg_list)

        return True

    def _send_messages(self, room_name, msg_list):
        u""" 部屋に対してメッセージを送る """
        for sessid, socket in self.socket.server.sockets.iteritems():
            if room_name in socket.session['room_list']:
                for msg in msg_list:
                    if msg.is_target_user(socket.session.get("user")):
                        pkt = dict(type="event",
                                   name="message",
                                   args=msg.to_dict(),
                                   endpoint=self.ns_name)
                        socket.send_packet(pkt)

    def recv_connect(self):
        u""" クライアント接続時に認証して session["user"] をセットする """
        auth_token = self._get_auth_token(self.request)
        if not auth_token:
            self.error('connection failed', u'接続に失敗しました')
            self.disconnect()
            return

        self.session["user"] = auth_token.client_session.user

    def recv_disconnect(self):
        self.disconnect(silent=True)
        return True

    def _get_auth_token(self, request):
        u""" request を元に AccessToken オブジェクトを返す """
        repo_token = request.context.repos['access_token']
        token = request.params.get('access_token', None)
        if not token:
            return None
        try:
            auth_token = repo_token.get_by_token(token)
            if auth_token.is_revoked():
                return None
        except ValueError:
            return None
        return auth_token



@view_config(route_name='socketio', permission='everyone')
def socketio_service(context, request):
    try:
        # request.context = context
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        logger.error("Exception while handling socketio connection",
                     exc_info=True)
    return Response()
