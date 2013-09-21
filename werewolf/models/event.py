""" event """
from django.db import models
from django_extensions.db.fields.json import JSONField

from .base import EntityModel


class Event(EntityModel):
    """ event """
    TYPE_MESSAGE = "message"
    TYPE_EXECUTION = "execution"
    TYPE_SET_EXECUTION = "set_execution"
    TYPE_GAME_START = "game_start"

    EVENT_TYPE_CHOICES = (
        (TYPE_MESSAGE, 'message'),
        (TYPE_EXECUTION, 'execution'),
        (TYPE_SET_EXECUTION, 'set execution'),
        (TYPE_GAME_START, 'game_start'),
    )

    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default=TYPE_MESSAGE)
    user = models.ForeignKey('User', null=True)
    player = models.ForeignKey('Player', null=True)
    village = models.ForeignKey('Village')
    value = JSONField()

    class Meta:
        app_label = 'werewolf'
