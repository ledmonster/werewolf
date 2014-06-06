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


class Event(EntityModel):
    """ event """

    event_type = models.CharField(max_length=32, choices=EventType.LABELS, default=EventType.MESSAGE)
    user = models.ForeignKey('User', null=True)
    resident = models.ForeignKey('Resident', null=True)
    village = models.ForeignKey('Village')
    value = JSONField()

    class Meta:
        app_label = 'werewolf'
