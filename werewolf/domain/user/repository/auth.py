# -*- coding: utf-8 -*-
from werewolf.domain.base import Identity
from werewolf.domain.user import *


class AccessTokenRepository(object):
    u""" AccessToken の Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_token(self, token):
        return self.engine(AccessToken).filter(token=token).one()

    def add(self, entity):
        if not isinstance(entity, AccessToken):
            raise ValueError
        self.engine.save(entity)
        return entity


class RefreshTokenRepository(object):
    u""" RefreshToken の Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_token(self, token):
        return self.engine(RefreshToken).filter(token=token).one()

    def add(self, entity):
        if not isinstance(entity, RefreshToken):
            raise ValueError
        self.engine.save(entity)
        return entity


class ClientSessionRepository(object):
    u""" ClientSession リポジトリ """

    def __init__(self, engine):
        self.engine = engine

    def get(self, identity):
        identity = Identity(identity)
        return self.engine(ClientSession).filter(identity=identity).one()

    def create(self, user_id):
        entity = ClientSession(user_id=user_id)
        self.engine.save(entity)
        return entity
