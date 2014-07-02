# -*- coding: utf-8 -*-

from werewolf.domain.user.models import *


class UserRepository(object):
    u""" ユーザに関する処理を行う Repository """

    def get(self, user_id):
        return User.objects.get(identity=user_id)

    def get_by_name(self, name):
        return User.objects.get(name=name)

    def update_name(self, user_id, new_name):
        user = self.get(user_id)
        user.name = new_name
        user.save()
        return user
