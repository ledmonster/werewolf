# -*- encoding: utf-8 -*-
""" event """
from django.db import models
from django_extensions.db.fields.json import JSONField

from .base import EntityModel, ValueObject


class EventType(ValueObject):
    MESSAGE = "message"
    EXECUTION = "execution"
    SET_EXECUTION = "set_execution"
    GAME_START = "game_start"

    LABELS = (
        (MESSAGE, 'message'),
        (EXECUTION, 'execution'),
        (SET_EXECUTION, 'set execution'),
        (GAME_START, 'game_start'),
    )


class EventRepository(EntityModel):
    """ event """

    event_type = models.CharField(max_length=32, choices=EventType.LABELS, default=EventType.MESSAGE)
    user = models.ForeignKey('User', null=True)
    village = models.ForeignKey('Village')
    generation = models.IntegerField()
    content = JSONField(null=True)

    class Meta:
        app_label = 'werewolf'
        db_table = 'werewolf_event'
