# -*- coding: utf-8 -*-
from werewolf.exception import GameException
from werewolf.game import Game
from werewolf.models import *


class MessageHandler(object):
    u"""
    @join     ゲームに参加する（未開始時のみ有効）
    @leave    ゲームから抜ける（未開始時のみ有効）
    @start:   ゲームを開始する
    @reset:   ゲームをリセットする
    @set:     処刑対象をセット
    @attack:  襲撃対象をセット
    @hunt:    道連れ対象をセット（自分が死ぬときに発動）
    @fortune: 占い対象をセット
    @state:   ゲームの状態確認
    @help:    ヘルプ表示
    """

    @classmethod
    def dispatch(cls, village_id, user, msg):
        u""" メッセージを各処理に振り分ける """
        msg = msg.strip()
        if msg.startswith("@"):
            cmd_name = msg.split()[0][1:]
            cmd_args = msg.split()[1:]
            method_name = "do_%s" % cmd_name
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                return method(village_id, user, msg, cmd_args)
            else:
                return cls.do_help(village_id, user, msg, cmd_args)
        else:
            return cls.do_message(village_id, user, msg, [])

    @classmethod
    def do_message(cls, village_id, user, msg, args):
        u"""
        メッセージを送信する。
        ゲーム開始状態でなければ誰でもメッセージを送れるが、
        ゲーム開始状態の場合は生きている参加者しかメッセージを送れない。
        (独り言として扱われる)
        """
        village = Village.objects.get(identity=village_id)
        if village.status == VillageStatus.OUT_GAME:
            return Message(msg, sender=user)
        else:
            resident = Resident.objects.get(
                village=village, user=user, generation=village.generation)
            if resident.status == ResidentStatus.ALIVE:
                return Message(msg, sender=user)
        return Message(u"現在メッセージは送れません。", sender=None, receiver=user)

    @classmethod
    def do_join(cls, village_id, user, msg, args):
        game = Game(village_id)
        resident, created = game.add_resident(user)
        if created:
            return Message(u"%s さんが村に参加しました" % user.name)
        return Message(
            u"%s さんは既に村に参加しています" % user.name, None, user)

    @classmethod
    def do_leave(cls, village_id, user, msg, args):
        game = Game(village_id)
        village = Village.objects.get(identity=village_id)
        try:
            resident = game.get_resident(user)
        except GameException as e:
            return Message(unicode(e), None, user)
        if village.status == VillageStatus.IN_GAME:
            return Message(u"ゲーム中は村から出られません。", None, user)
        game.remove_resident(resident)
        return Message(u"%s さんが村から出ました" % user.name)

    @classmethod
    def do_start(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            village = game.start()
        except GameException as e:
            return Message(unicode(e), None, user)
        residents = village.resident_set.all()
        messages = []
        messages.append(Message(u"さあ、第%s回目のゲームの始まりです。" % village.generation))
        for r in residents:
            messages.append(
                Message(u"あなたは「%s」です" % r.get_role_display(), None, r.user))
        return messages

    @classmethod
    def do_reset(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            village = game.reset()
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"第%d回のゲームをリセットしました" % village.generation)

    @classmethod
    def do_night(cls, village_id, user, msg, args):
        return cls.do_message(cls, village_id, user, msg)

    @classmethod
    def do_set(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_execution_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を吊り対象にセットしました" % target_name, None, user)

    @classmethod
    def do_attack(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_attack_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を襲撃対象にセットしました" % target_name, None, user)

    @classmethod
    def do_hunt(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_hunt_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を道連れ対象にセットしました" % target_name, None, user)

    @classmethod
    def do_fortune(cls, village_id, user, msg, args):
        game = Game(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_fortune_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を占い対象にセットしました" % target_name, None, user)

    @classmethod
    def do_state(cls, village_id, user, msg, args):
        game = Game(village_id)
        village = Village.objects.get(identity=village_id)
        residents = game.get_residents()
        contents = []

        contents.append(u"■%s （第%d回：%s）" % (village.name, village.generation, village.get_status_display()))

        if village.status == VillageStatus.IN_GAME:
            try:
                resident = game.get_resident(user)
                contents.append(u"あなたは「%s」です。（%s）" % (resident.get_role_display(), resident.get_status_display()))
            except GameException as e:
                pass

        contents.append("")
        contents.append(u"■住人")
        contents.append("\n".join([u"- %s （%s）" % (r.user.name, r.get_status_display()) for r in residents]))

        from werewolf.websocketserver import clients
        contents.append("")
        contents.append(u"■接続ユーザ")
        contents.append("\n".join(["- %s" % c.user.name for c in clients[village_id]]))

        return Message("\n".join(contents), None, user)

    @classmethod
    def do_help(cls, village_id, user, msg, args):
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
        default_avatar = "http://www.gravatar.com/avatar/?f=y&s=30"
        return dict(
            content = self.content,
            sender_id = self.sender and self.sender.identity or None,
            sender_name = self.sender and self.sender.name or "system",
            sender_color = self.sender and self.sender.color or "#000000",
            sender_avatar = self.sender and self.sender.get_avatar_url(30) or default_avatar,
            receiver_id = self.receiver and self.receiver.identity or None,
        )
