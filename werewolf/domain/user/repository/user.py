# -*- coding: utf-8 -*-
import uuid

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
        if isinstance(identity, basestring):
            identity = uuid.UUID(hex=identity)
        elif isinstance(identity, int):
            identity = uuid.UUID(int=identity)
        elif not isinstance(identity, uuid.UUID):
            raise ValueError
        return self.engine(User).filter(identity=identity).one()

    def get_by_name(self, name):
        return self.engine(User).filter(name=name).one()

    def get_by_email(self, email):
        return self.engine(User).filter(email=email).one()


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
