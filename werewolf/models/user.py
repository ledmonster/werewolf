# -*- encoding: utf-8 -*-
""" user """
import urllib, hashlib

from django.db import models
from django_extensions.db.models import TimeStampedModel

from .base import EntityModel, ValueObject


class UserStatus(ValueObject):
    ENABLED = 1
    DISABLED = 2

    LABELS = (
        (ENABLED, u'有効'),
        (DISABLED, u'無効'),
    )


class CredentialType(ValueObject):
    GOOGLE = 1

    LABELS = (
        (GOOGLE, 'google'),
    )


class User(EntityModel):
    """ user """

    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    hue = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(choices=UserStatus.LABELS, default=UserStatus.ENABLED)

    def get_avatar_url(self, size):
        return "http://www.gravatar.com/avatar/{}?s={:d}".format(
            hashlib.md5(self.email.lower()).hexdigest(), size)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'werewolf'


class UserCredential(TimeStampedModel):
    """ user credential """

    # django doesn't support multiple primary key
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User')
    credential_type = models.SmallIntegerField(choices=CredentialType.LABELS)
    key = models.CharField(max_length=128)
    secret = models.CharField(max_length=128, blank=True)

    class Meta:
        app_label = 'werewolf'
