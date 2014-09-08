# -*- coding: utf-8 -*-

from werewolf.domain.user.models import *


class UserRepository(object):
    u""" ユーザに関する処理を行う Repository """

    def __init__(self, engine):
        self.engine = engine

    def get_by_name(self, name):
        return self.engine(User).filter(name=name).one()
