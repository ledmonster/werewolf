# -*- coding: utf-8 -*-
import logging

from pyramid.response import Response
from pyramid.view import view_config
from socketio.namespace import BaseNamespace
from socketio import socketio_manage
from socketio.mixins import BroadcastMixin, RoomsMixin

from werewolf.domain.user.models import *


logger = logging.getLogger(__name__)


class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.logger = logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, room):
        self.room = room
        self.join(room)
        return True

    def on_nickname(self, nickname):
        self.log('Nickname: {0}'.format(nickname))
        self.nicknames.append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_connect(self):
        u""" クライアント接続時に認証して self.user をセットする """
        auth_token = self._get_auth_token(self.request)
        if not auth_token:
            self.error('connection failed', u'接続に失敗しました')
            self.disconnect()
            return

        self.user = auth_token.client_session.user

    def _get_auth_token(self, request):
        u""" request を元に AccessToken オブジェクトを返す """
        token = request.params.get('access_token', None)
        if not token:
            return None
        try:
            auth_token = AccessToken.objects.get(token=token)
            if auth_token.is_revoked():
                return None
        except AccessToken.DoesNotExist:
            return None
        return auth_token

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        nickname = self.socket.session['nickname']
        self.nicknames.remove(nickname)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', self.nicknames)
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
            self.socket.session['nickname'], msg)
        return True


@view_config(route_name='socketio', permission='everyone')
def socketio_service(request):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        logger.error("Exception while handling socketio connection",
                     exc_info=True)
    return Response()
