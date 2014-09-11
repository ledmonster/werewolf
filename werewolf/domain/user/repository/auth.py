# -*- coding: utf-8 -*-
import uuid

from werewolf.domain.user.models import *


class AccessTokenRepository(object):
    u""" AccessToken の Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_token(self, token):
        return self.engine(AccessToken).filter(token=token).one()

    def save(self, entity):
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

    def save(self, entity):
        if not isinstance(entity, RefreshToken):
            raise ValueError
        self.engine.save(entity)
        return entity


class ClientSessionRepository(object):
    u""" ClientSession リポジトリ """

    def __init__(self, engine):
        self.engine = engine

    def get(self, identity):
        if isinstance(identity, basestring):
            identity = uuid.UUID(hex=identity)
        elif isinstance(identity, int):
            identity = uuid.UUID(int=identity)
        elif not isinstance(identity, uuid.UUID):
            raise ValueError
        return self.engine(ClientSession).filter(identity=identity).one()

    def create(self, user_id):
        entity = ClientSession(user_id=user_id)
        self.engine.save(entity)
        return entity
