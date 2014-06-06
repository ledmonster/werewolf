# -*- encoding: utf-8 -*-
""" event """
from django.db import models
from django_extensions.db.fields.json import JSONField

from .base import EntityModel, ValueObject


class EventType(ValueObject):
    MESSAGE = "message"
    JOIN = "join"
    LEAVE = "leave"
    START = "start"
    END = "end"
    RESET = "reset"
    NIGHT = "night"
    MORNING = "morning"

    LABELS = (
        (MESSAGE, u'メッセージ'),
        (JOIN, u'参加'),
        (LEAVE, u'離脱'),
        (START, u'ゲーム開始'),
        (END, u'ゲーム終了'),
        (RESET, u'ゲームリセット'),
        (NIGHT, u'夜のターン'),
        (MORNING, u'朝のターン'),
    )


class EventModel(EntityModel):
    """ event """

    event_type = models.CharField(max_length=32, choices=EventType.LABELS, default=EventType.MESSAGE)
    user = models.ForeignKey('User', null=True)
    village = models.ForeignKey('VillageModel')
    generation = models.IntegerField()
    content = JSONField(null=True)

    class Meta:
        app_label = 'werewolf'
        db_table = 'werewolf_event'
