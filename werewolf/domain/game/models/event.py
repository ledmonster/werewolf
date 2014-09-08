# -*- coding: utf-8 -*-

from werewolf.domain.game.models.event_model import EventModel, EventType

class Event(object):
    u""" イベントのベースクラス """
    pass


class EternalEvent(Event):
    u""" 永続化するイベント """
    def to_model(self):
        raise NotImplementedError


# class EphemeralEvent(Event):
#     u""" 永続化しないイベント """
#     pass


# class GameErrorEvent(EphemeralEvent):
#     u""" ユーザの誤った操作をたしなめるイベント """
#     def __init__(self, message):
#         self.message = message


class MessageEvent(EternalEvent):
    u""" メッセージ送信イベント """
    def __init__(self, village, user, message):
        self.village = village
        self.user = user
        self.message = message

    @property
    def content(self):
        return {"message": self.message}

    def to_model(self):
        return EventModel(
            event_type=EventType.MESSAGE,
            user_id=self.user.identity,
            village_id=self.village.identity,
            generation=self.village.generation,
            content=self.content);


class JoinEvent(EternalEvent):
    u""" 参加イベント """
    def __init__(self, resident):
        self.resident = resident

    @property
    def content(self):
        return {"resident": self.resident.identity}

    def to_model(self):
        return EventModel(
            event_type=EventType.JOIN,
            user_id=self.resident.user.identity,
            village_id=self.resident.village.identity,
            generation=self.resident.generation,
            content=self.content);


class LeaveEvent(EternalEvent):
    u""" 離脱イベント """
    def __init__(self, resident):
        self.resident = resident

    @property
    def content(self):
        return {"resident": self.resident.identity}

    def to_model(self):
        return EventModel(
            event_type=EventType.LEAVE,
            user_id=self.resident.user.identity,
            village_id=self.resident.village.identity,
            generation=self.resident.generation,
            content=self.content);


class GameStartEvent(EternalEvent):
    u""" ゲーム開始イベント """
    def __init__(self, village):
        self.village = village

    @property
    def content(self):
        return {}

    def to_model(self):
        return EventModel(
            event_type=EventType.START,
            user_id=None,
            village_id=self.village.identity,
            generation=self.village.generation,
            content=self.content);


class GameEndEvent(EternalEvent):
    u""" ゲーム終了イベント """
    def __init__(self, village, winner):
        self.village_id = village
        self.winner = winner

    @property
    def content(self):
        return {"winner": self.winner.value}

    def to_model(self):
        return EventModel(
            event_type=EventType.END,
            user_id=None,
            village_id=self.village.identity,
            generation=self.village.generation,
            content=self.content);


class GameResetEvent(EternalEvent):
    u""" ゲームリセットイベント """
    def __init__(self, new_village):
        self.new_village = new_village

    @property
    def content(self):
        return {}

    def to_model(self):
        return EventModel(
            event_type=EventType.RESET,
            user_id=None,
            village_id=self.new_village.identity,
            generation=self.new_village.generation-1,  # record previous generation
            content=self.content);


class NightEvent(EternalEvent):
    u""" 夜イベント """
    def __init__(self, village, targets):
        self.village = village
        self.targets = targets

    @property
    def content(self):
        return dict([(k, v.identity) for k, v in self.targets.iteritems() if v])

    def to_model(self):
        return EventModel(
            event_type=EventType.NIGHT,
            user_id=None,
            village_id=self.village.identity,
            generation=self.village.generation,
            content=self.content);


class MorningEvent(EternalEvent):
    u""" 朝イベント """
    def __init__(self, village):
        self.village = village

    @property
    def content(self):
        return {"day": self.village.day}

    def to_model(self):
        return EventModel(
            event_type=EventType.MORNING,
            user_id=None,
            village_id=self.village.identity,
            generation=self.village.generation,
            content=self.content);
