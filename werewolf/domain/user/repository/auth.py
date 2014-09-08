# -*- coding: utf-8 -*-
from werewolf.domain.user.models import *


class AccessTokenRepository(object):
    u""" AccessToken の Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_token(self, token):
        return self.engine(AccessToken).filter(token=token).one()


class CrientSessionRepository(object):
    u""" CrientSession リポジトリ """

    def __init__(self, engine):
        self.engine = engine

    def create(self, user_id):
        entity = CrientSession(user_id=user_id)
        self.engine(CrientSession).save(entity)
