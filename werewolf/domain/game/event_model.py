# -*- coding: utf-8 -*-
""" event """
from flywheel import Model, Field
from flywheel.fields.types import STRING

from werewolf.domain.base import EntityModel, ValueObject, register_enum_type
from werewolf.domain.user.repository import get_repository


class EventType(ValueObject):
    MESSAGE = "message"
    JOIN = "join"
    LEAVE = "leave"
    START = "start"
    END = "end"
    RESET = "reset"
    NIGHT = "night"
    MORNING = "morning"

    class Labels:
        MESSAGE = u'メッセージ'
        JOIN = u'参加'
        LEAVE = u'離脱'
        START = u'ゲーム開始'
        END = u'ゲーム終了'
        RESET = u'ゲームリセット'
        NIGHT = u'夜のターン'
        MORNING = u'朝のターン'

register_enum_type(EventType, STRING)


class EventModel(EntityModel):
    u""" event """

    event_type = Field(data_type='EventType')
    user_id = Field(data_type='identity')
    village_id = Field(data_type='identity')
    generation = Field(data_type=int)
    content = Field(data_type=dict)

    __metadata__ = {
        'name': 'event',
    }

    @property
    def user(self):
        return ge# -*- coding: utf-8 -*-
""" event """
