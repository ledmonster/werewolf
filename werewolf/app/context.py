# -*- coding: utf-8 -*-
from pyramid.security import Allow, Everyone, Authenticated

from werewolf.domain.user.repository import UserRepository
from werewolf.domain.game.repository import (
    VillageRepository,
    EventRepository,
    BehaviorRepository,
)


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
            "village": VillageRepository(self.engine),
            "event": EventRepository(self.engine),
            "behavior": BehaviorRepository(self.engine),
        }

    @property
    def repos(self):
        return self._repos
