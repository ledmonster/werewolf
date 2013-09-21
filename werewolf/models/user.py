""" user """
from django.db import models
from django_extensions.db.models import TimeStampedModel

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


class UserCredential(TimeStampedModel):
    """ user credential """
    CREDENTIAL_TYPE_GOOGLE = 1
    CREDENTIAL_TYPE_CHOICES = (
        (CREDENTIAL_TYPE_GOOGLE, 'google'),
    )

    # django doesn't support multiple primary key
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User')
    credential_type = models.SmallIntegerField(choices=CREDENTIAL_TYPE_CHOICES)
    key = models.CharField(max_length=128)
    secret = models.CharField(max_length=128, blank=True)

    class Meta:
        app_label = 'werewolf'
