# -*- coding: utf-8 -*-
from werewolf.domain.base import Identity
from werewolf.domain.user.models import *


class UserRepository(object):
    u""" ユーザに関する処理を行う Repository """

    def __init__(self, engine):
        self.engine = engine

    def create(self, **params):
        user = User(**params)
        self.engine.save(user)
        return user

    def get(self, identity):
        identity = Identity(identity)
        return self.engine(User).filter(identity=identity).one()

    def get_by_name(self, name):
        try:
            return self.engine.scan(User).filter(name=unicode(name)).all()[0]
        except IndexError:
            raise ValueError('user not found. name: {}'.format(name))

    def get_by_email(self, email):
        return self.engine(User).filter(email=email).one()

    def update(self, entity):
        self.engine.sync(entity)
        return entity


class UserCredentialRepository(object):
    u""" UserCredential のリポジトリ """

    def __init__(self, engine):
        self.engine = engine

    def create(self, user_id, credential_type, key):
        entity = UserCredential(
            user_id=user_id,
            credential_type=credential_type,
            key=key
        )
        self.engine.save(entity)

    def get(self, credential_type, key):
        return self.engine(UserCredential).filter(
            credential_type=credential_type, key=key).one()
