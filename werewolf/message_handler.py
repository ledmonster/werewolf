# -*- coding: utf-8 -*-
from werewolf.models import *


class MessageHandler(object):
    u"""
    @set:    処刑対象をセット
    @attack: 襲撃対象をセット
    @state:  ゲームの状態確認
    @help:   ヘルプ表示
    """

    @classmethod
    def dispatch(cls, village_id, user, msg):
        msg = msg.strip()
        if msg.startswith("@"):
            cmd_name = msg.split()[0][1:]
            method_name = "do_%s" % cmd_name
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                return method(village_id, user, msg)
            else:
                return cls.do_help(village_id, user, msg)
        else:
            return cls.do_message(village_id, user, msg)

    @classmethod
    def do_message(cls, village_id, user, msg):
        village = Village.objects.get(identity=village_id)
        if village.status == VillageStatus.OUT_GAME:
            return Message(msg, sender=user)
        else:
            resident = Resident.objects.get(village=village, user=user)
            if resident.status == ResidentStatus.ALIVE:
                return Message(msg, sender=user)
        return Message(msg, sender=user, receiver=user)

    @classmethod
    def do_set(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_attack(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_join(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_leave(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_start(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_end(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_night(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_state(cls, village_id, user, msg):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_help(cls, village_id, user, msg):
        content = cls.__doc__.strip()
        return Message(content, None, user)


class Message(object):
    u""" Client へ返す Message を格納するクラス
    sender が None の場合はシステムからのメッセージで、
    receiver が None の場合は全員に対してメッセージを送る。
    """

    def __init__(self, content, sender=None, receiver=None):
        self.content = content
        self.sender = sender
        self.receiver = receiver

    def is_target_user(self, user):
        if self.receiver is None:
            return True
        elif self.receiver.identity == user.identity:
            return True
        return False

    def to_dict(self):
        return dict(
            content = self.content,
            sender_id = self.sender and self.sender.identity or None,
            sender_name = self.sender and self.sender.name or "system",
            sender_color = self.sender and self.sender.color or "#000000",
            receiver_id = self.receiver and self.receiver.identity or None,
        )
