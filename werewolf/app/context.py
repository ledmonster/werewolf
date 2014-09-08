# -*- coding: utf-8 -*-
from flywheel import Engine
from pyramid.security import Allow, Everyone, Authenticated

from werewolf.app.message_handler import MessageHandler
from werewolf.domain.user.repository import *
from werewolf.domain.game.repository import *


class RootFactory(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, 'everyone'),
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        self.engine = Engine()
        self.engine.connect_to_host(host='localhost', port=8000, is_secure=False)

        self._repos = {
            "user": UserRepository(self.engine),
            "user_credential": UserCredentialRepository(self.engine),
            "access_token": AccessTokenRepository(self.engine),
            "refresh_token": RefreshTokenRepository(self.engine),
            "client_session": ClientSessionRepository(self.engine),
            "village": VillageRepository(self.engine),
            "event": EventRepository(self.engine),
            "behavior": BehaviorRepository(self.engine),
        }
        self._message_handler = MessageHandler(self)

    @property
    def repos(self):
        return self._repos

    @property
    def message_handler(self):
        return self._message_handler
