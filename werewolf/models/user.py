""" user """
import uuid

from django.db import models
from uuidfield import UUIDField

class User(models.Model):
    """ user """
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    STATUS_CHOICES = (
        (STATUS_ENABLED, 'enabled'),
        (STATUS_DISABLED, 'disabled'),
    )

    identity = UUIDField(auto=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ENABLED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'
