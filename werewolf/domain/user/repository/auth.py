# -*- coding: utf-8 -*-
from werewolf.domain.user.models import *


class AccessTokenRepository(object):
    u""" AccessToken の Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_token(self, token):
        return self.engine(AccessToken).filter(token=token).one()


class ClientSessionRepository(object):
    u""" ClientSession リポジトリ """

    def __init__(self, engine):
        self.engine = engine

    def get(self, identity):
        return self.engine(ClientSession).filter(identity=identity).one()

    def create(self, user_id):
        entity = ClientSession(user_id=user_id)
        self.engine.save(entity)
        return entity
