""" user """
import uuid

from django.db import models
from uuidfield import UUIDField

class User(models.Model):
    """ user """
    identity = UUIDField(auto=True, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
      app_label = 'werewolf'
