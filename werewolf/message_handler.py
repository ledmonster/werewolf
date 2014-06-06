# -*- coding: utf-8 -*-
u""" メッセージの処理を行うモジュール。この中でモデルの操作はしない。 """
import collections

from werewolf.exception import GameException, GameNotFinished
from werewolf.domain import *
from werewolf.models import *


class MessageHandler(object):
    u"""
    @join     ゲームに参加する（未開始時のみ有効）
    @leave    ゲームから抜ける（未開始時のみ有効）
    @start:   ゲームを開始する
    @night:   夜を開始する
    @reset:   ゲームをリセットする
    @set:     処刑対象をセット
    @attack:  襲撃対象をセット
    @hunt:    道連れ対象をセット（自分が死ぬときに発動）
    @fortune: 占い対象をセット
    @state:   ゲームの状態確認
    @help:    ヘルプ表示
    """

    @classmethod
    def get_auth_error_message(cls):
        return Message(u"認証に失敗しました")

    @classmethod
    def get_comming_message(cls, user):
        return Message(u"%s さんが村にやってきました" % user.name)

    @classmethod
    def get_leaving_message(cls, user):
        return Message(u"%s さんが村を立ち去りました" % user.name)

    @classmethod
    def get_initial_messages(cls, village_id, user):
        u"""
        接続時に過去メッセージを取得する
        TODO: user を使う
        """
        game = Game.get_instance(village_id)
        events = game.get_current_events()

        messages = []
        for e in events:
            if e.event_type == EventType.MESSAGE:
                message = Message(e.content["message"], e.user)
            elif e.event_type == EventType.JOIN:
                message = Message(u"%s さんが村に参加しました" % e.user.name)
            elif e.event_type == EventType.LEAVE:
                message = Message(u"%s さんが村から出ました" % e.user.name)
            elif e.event_type == EventType.START:
                message = Message(u"さあ、第%s回目のゲームの始まりです。" % e.generation)
                # TODO: logic
            elif e.event_type == EventType.END:
                # skip, because game is ended
                continue
            elif e.event_type == EventType.RESET:
                # skip, because game is ended
                continue
            elif e.event_type == EventType.NIGHT:
                # TODO: logic
                message = Message(u"夜になりました（履歴未実装 ...）")
            elif e.event_type == EventType.MORNING:
                message = Message(u"新しい朝がきました。%d日目です。" % e.content["day"])
            messages.append(message)
        return messages

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
        game = Game.get_instance(village_id)
        try:
            msg_event = game.store_message(user, msg)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(msg_event.message, user)

    @classmethod
    def do_join(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            resident = game.join(user)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s さんが村に参加しました" % user.name)

    @classmethod
    def do_leave(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            game.leave(user)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s さんが村から出ました" % user.name)

    @classmethod
    def do_start(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            village = game.start()
        except GameException as e:
            return Message(unicode(e), None, user)
        residents = game.get_residents()
        messages = []
        messages.append(Message(u"さあ、第%s回目のゲームの始まりです。" % village.generation))
        for r in residents:
            messages.append(
                Message(u"あなたは「%s」です" % r.get_role_display(), None, r.user))
        return messages

    @classmethod
    def do_reset(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            village = game.reset()
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"第%d回のゲームをリセットしました" % village.generation)

    @classmethod
    def do_night(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            targets = game.execute_night()
        except GameException as e:
            return Message(unicode(e), None, user)

        messages = []
        for k, t in targets.iteritems():
            if t is not None:
                if k == BehaviorType.EXECUTION:
                    messages.append(Message(u"%s が吊られました" % t.user.name))
                elif k == BehaviorType.ATTACK:
                    messages.append(Message(u"%s が襲撃されました" % t.user.name))
                elif k == BehaviorType.HUNT:
                    messages.append(Message(u"%s が道連れになりました" % t.user.name))
                elif k == BehaviorType.FORTUNE:
                    # 死んでても知らせる
                    tellers = game.get_residents(role=Role.TELLER)
                    for t in tellers:
                        messages.append(
                            Message(u"%s は「%s」です" % (t.user.name, t.get_role_display()), None, t.user))

        # ゲーム終了、または翌日へ
        if game.satisfy_game_end():
            winner = game.get_winner()
            residents = game.get_residents()

            messages.append(
                Message(
                    u"%sチームの勝ちです\n" % winner.label +
                    "\n".join([u"・%s ： %s（%s）" %
                               (r.user.name, r.get_role_display(), r.get_status_display()) for r in residents])))
            village = game.end()
        else:
            village = game.execute_morning()
            messages.append(Message(u"新しい朝がきました。%d日目です。" % village.day))

        return messages

    @classmethod
    def do_set(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_execution_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を吊り対象にセットしました" % target_name, None, user)

    @classmethod
    def do_attack(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_attack_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を襲撃対象にセットしました" % target_name, None, user)

    @classmethod
    def do_hunt(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_hunt_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を道連れ対象にセットしました" % target_name, None, user)

    @classmethod
    def do_fortune(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        try:
            target_name = args and args[0] or ""
            game.set_fortune_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"%s を占い対象にセットしました" % target_name, None, user)

    @classmethod
    def do_state(cls, village_id, user, msg, args):
        game = Game.get_instance(village_id)
        village = game.village
        residents = game.get_residents()
        contents = []

        contents.append(u"【第%d回 %s】 （%s）" % (village.generation, village.name, village.get_status_display()))

        if game.in_game():
            roles = game.get_role_constitution()
            contents.append(u"住人構成：%s" % ", ".join([r.label for r in roles]))
            try:
                resident = game.get_resident(user)
                contents.append(u"あなたは「%s」です。（%s）" % (resident.get_role_display(), resident.get_status_display()))
            except GameException as e:
                pass

        if residents:
            contents.append("")
            contents.append(u"■住人")
            contents.append("\n".join([u"・%s （%s）" % (r.user.name, r.get_status_display()) for r in residents]))

        from werewolf.websocketserver import clients
        users = collections.Counter([c.user for c in clients[village_id]])
        contents.append("")
        contents.append(u"■接続ユーザ")
        contents.append("\n".join([u"・%s （%d接続）" % (u, n) for u, n in users.iteritems()]))

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
            sender_name = self.sender and self.sender.name or u"★Game Master★",
            sender_hue = self.sender and self.sender.hue or 0,
            sender_avatar = self.sender and self.sender.get_avatar_url(30) or default_avatar,
            receiver_id = self.receiver and self.receiver.identity or None,
        )
