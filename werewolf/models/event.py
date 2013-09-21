""" event """
import uuid

from django.db import models
from uuidfield import UUIDField
from jsonfield import JSONField


class Event(models.Model):
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

    identity = UUIDField(version=1, auto=True, primary_key=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES, default=TYPE_MESSAGE)
    user = models.ForeignKey('User', null=True)
    player = models.ForeignKey('Player', null=True)
    village = models.ForeignKey('Village')
    value = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'
