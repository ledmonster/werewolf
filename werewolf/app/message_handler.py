# -*- coding: utf-8 -*-
u""" メッセージの処理を行うモジュール。この中でモデルの操作はしない。 """
import collections

from werewolf.domain.game.exception import GameException, GameNotFinished
from werewolf.domain.game.models import GameService, EventType, BehaviorType


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

    def __init__(self, context):
        self.context = context

    def get_auth_error_message(self):
        return Message(u"認証に失敗しました")

    def get_coming_message(self, user):
        return Message(u"{} さんが村にやってきました".format(user.name))

    def get_leaving_message(self, user):
        return Message(u"{} さんが村を立ち去りました".format(user.name))

    def get_initial_messages(self, village_id, user):
        u""" 接続時に過去メッセージを取得する """
        game = GameService(self.context, village_id)
        events = game.get_current_events()

        messages = []
        for e in events:
            if e.event_type is EventType.MESSAGE:
                message = Message(e.content["message"], e.user)
            elif e.event_type is EventType.JOIN:
                message = Message(u"{} さんが村に参加しました".format(e.user.name))
            elif e.event_type is EventType.LEAVE:
                message = Message(u"{} さんが村から出ました".format(e.user.name))
            elif e.event_type is EventType.START:
                message = Message(u"さあ、第{}回目のゲームの始まりです。".format(e.generation))
                # TODO: logic
            elif e.event_type is EventType.END:
                # skip, because game is ended
                continue
            elif e.event_type is EventType.RESET:
                # skip, because game is ended
                continue
            elif e.event_type is EventType.NIGHT:
                # TODO: logic
                message = Message(u"夜になりました（履歴未実装 ...）")
            elif e.event_type is EventType.MORNING:
                message = Message(u"新しい朝がきました。{:d}日目です。".format(e.content["day"]))
            messages.append(message)
        return messages

    def dispatch(self, village_id, user, msg):
        u""" メッセージを各処理に振り分ける """
        msg = msg.strip()
        if msg.startswith("@"):
            cmd_name = msg.split()[0][1:]
            cmd_args = msg.split()[1:]
            method_name = "do_" + cmd_name
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                return method(village_id, user, msg, cmd_args)
            else:
                return self.do_help(village_id, user, msg, cmd_args)
        else:
            return self.do_message(village_id, user, msg, [])

    def do_message(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            msg_event = game.store_message(user, msg)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(msg_event.message, user)

    def do_join(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            resident = game.join(user)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} さんが村に参加しました".format(user.name))

    def do_leave(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            game.leave(user)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} さんが村から出ました".format(user.name))

    def do_start(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            village = game.start()
        except GameException as e:
            return Message(unicode(e), None, user)
        residents = game.village.get_residents()
        messages = []
        messages.append(Message(u"さあ、第{}回目のゲームの始まりです。".format(village.generation)))
        for r in residents:
            messages.append(
                Message(u"あなたは「{role.label}」です".format(role = r.role), None, r.user))
        return messages

    def do_reset(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            village = game.reset()
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"第{:d}回のゲームをリセットしました".format(village.generation))

    def do_night(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            targets = game.execute_night()
        except GameException as e:
            return Message(unicode(e), None, user)

        messages = []
        for k, t in targets.iteritems():
            if t is not None:
                if k == BehaviorType.EXECUTION.value:
                    messages.append(Message(u"{} が吊られました".format(t.user.name)))
                elif k == BehaviorType.ATTACK.value:
                    messages.append(Message(u"{} が襲撃されました".format(t.user.name)))
                elif k == BehaviorType.HUNT.value:
                    messages.append(Message(u"{} が道連れになりました".format(t.user.name)))
                elif k == BehaviorType.FORTUNE.value:
                    # 死んでても知らせる
                    tellers = game.village.get_residents(role=Role.TELLER)
                    for teller in tellers:
                        messages.append(
                            Message(u"{user.name} は「{role.label}」です".format(user=t.user, role=t.role), None, teller.user))

        # ゲーム終了、または翌日へ
        if game.satisfy_game_end():
            winner = game.get_winner()
            residents = game.village.get_residents()

            messages.append(
                Message(
                    u"{}チームの勝ちです\n".format(winner.label) +
                    "\n".join([u"・{user.name} ： {role.label}（{status.label}）".format(user=r.user, role=r.role, status=r.status)
                               for r in residents])))
            village = game.end()
        else:
            village = game.execute_morning()
            messages.append(Message(u"新しい朝がきました。{:d}日目です。".format(village.day)))

        return messages

    def do_set(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            target_name = args and args[0] or ""
            game.set_execution_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} を吊り対象にセットしました".format(target_name), None, user)

    def do_attack(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            target_name = args and args[0] or ""
            game.set_attack_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} を襲撃対象にセットしました".format(target_name), None, user)

    def do_hunt(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            target_name = args and args[0] or ""
            game.set_hunt_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} を道連れ対象にセットしました".format(target_name), None, user)

    def do_fortune(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        try:
            target_name = args and args[0] or ""
            game.set_fortune_target(user, target_name)
        except GameException as e:
            return Message(unicode(e), None, user)
        return Message(u"{} を占い対象にセットしました".format(target_name), None, user)

    def do_state(self, village_id, user, msg, args):
        game = GameService(self.context, village_id)
        village = game.village
        residents = game.village.get_residents()
        contents = []

        contents.append(u"【第{:d}回 {}】 （{}）".format(village.generation, village.name, village.status.label))

        if village.in_game():
            roles = game.get_role_constitution()
            contents.append(u"住人構成：{}".format(", ".join([r.label for r in roles])))
            try:
                resident = village.get_resident(user)
                if resident is not None:
                    contents.append(u"あなたは「{resident.role.label}」です。（{resident.status.label}）".format(resident=resident))
            except GameException as e:
                pass

        if residents:
            contents.append("")
            contents.append(u"■住人")
            contents.append("\n".join([u"・{} （{}）".format(r.user.name, r.status.label) for r in residents]))

        from pyramid.threadlocal import get_current_request
        current_socket = get_current_request().environ["socketio"]
        users = collections.Counter([
            s.session["user"]
            for s in current_socket.server.sockets.values()
            if "user" in s.session
        ])

        contents.append("")
        contents.append(u"■接続ユーザ")
        contents.append("\n".join([u"・{} （{:d}接続）".format(u.name, n) for u, n in users.iteritems()]))

        return Message("\n".join(contents), None, user)

    def do_help(self, village_id, user, msg, args):
        content = self.__doc__.strip()
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
            sender_id = self.sender and self.sender.identity.hex or None,
            sender_name = self.sender and self.sender.name or u"★Game Master★",
            sender_hue = self.sender and self.sender.hue or 0,
            sender_avatar = self.sender and self.sender.get_avatar_url(30) or default_avatar,
            receiver_id = self.receiver and self.receiver.identity.hex or None,
        )
