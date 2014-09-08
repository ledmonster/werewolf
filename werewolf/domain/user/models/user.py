# -*- coding: utf-8 -*-
""" user """
import datetime
import urllib, hashlib

# from django.db import models
# from django_extensions.db.models import TimeStampedModel
# from enumfields import EnumIntegerField
from flywheel import Model, Field
from flywheel.fields.types import NUMBER

from werewolf.domain.base import EntityModel, ValueObject, register_enum_type


class UserStatus(ValueObject):
    ENABLED = 1
    DISABLED = 2

    class Labels:
        ENABLED = u'有効'
        DISABLED = u'無効'


class CredentialType(ValueObject):
    GOOGLE = 1

    class Labels:
        GOOGLE = 'google'


register_enum_type(UserStatus, NUMBER)
register_enum_type(CredentialType, NUMBER)


class User(EntityModel):
    u""" user model """
    name = Field(data_type=unicode)
    email = Field(data_type=str, index='email-index')
    hue = Field(data_type=int)
    status = Field(data_type='UserStatus')

    @property
    def avatar_url_(self, size):
        return "http://www.gravatar.com/avatar/{}?s={:d}".format(
            hashlib.md5(self.email.lower()).hexdigest(), size)


class UserCredential(Model):
    u""" user credential model """
    user_id = Field(data_type='uuid', hash_key=True)
    credential_type = Field(data_type='CredentialType', index='credentail-type-index')
    key = Field(data_type=str)
    secret = Field(data_type=str)
    created = Field(data_type=datetime.datetime, range_key=True)


# class User(EntityModel):
#     """ user """

#     name = models.CharField(max_length=100, blank=True)
#     email = models.EmailField(blank=True)
#     hue = models.SmallIntegerField(default=0)
#     status = EnumIntegerField(UserStatus, default=UserStatus.ENABLED)

#     def get_avatar_url(self, size):
#         return "http://www.gravatar.com/avatar/{}?s={:d}".format(
#             hashlib.md5(self.email.lower()).hexdigest(), size)

#     def __unicode__(self):
#         return self.name

#     class Meta:
#         app_label = 'werewolf'


# class UserCredential(TimeStampedModel):
#     """ user credential """

#     # django doesn't support multiple primary key
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey('User')
#     credential_type = EnumIntegerField(CredentialType)
#     key = models.CharField(max_length=128)
#     secret = models.CharField(max_length=128, blank=True)

#     class Meta:
#         app_label = 'werewolf'
