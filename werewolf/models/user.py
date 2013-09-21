""" user """
from django.db import models

from .base import EntityModel


class User(EntityModel):
    """ user """
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    STATUS_CHOICES = (
        (STATUS_ENABLED, 'enabled'),
        (STATUS_DISABLED, 'disabled'),
    )

    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ENABLED)

    class Meta:
        app_label = 'werewolf'
