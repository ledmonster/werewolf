# -*- coding: utf-8 -*-

from werewolf.domain.user.models import *


class UserRepository(object):
    u""" ユーザに関する処理を行う Repository """

    def get_by_name(self, name):
        return User.objects.get(name=name)