# -*- encoding: utf-8 -*-

from werewolf.models import *

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
            user=self.user,
            village=self.village,
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
            user=self.resident.user,
            village=self.resident.village,
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
            user=self.resident.user,
            village=self.resident.village,
            generation=self.resident.generation,
            content=self.content);


class GameStartEvent(EternalEvent):
    u""" ゲーム開始イベント """
    pass


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
            user=None,
            village_id=self.new_village.identity,
            generation=self.new_village.generation-1,  # record previous generation
            content=self.content);


class NightEvent(EternalEvent):
    u""" 夜イベント """
    pass
