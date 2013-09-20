""" message """
import uuid

from django.db import models
from uuidfield import UUIDField


class Message(models.Model):
    """ message """
    identity = UUIDField(auto=True, primary_key=True)
    user = models.ForeignKey('User')
    player = models.ForeignKey('Player')
    village = models.ForeignKey('Village')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'
