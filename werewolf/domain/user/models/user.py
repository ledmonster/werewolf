# -*- coding: utf-8 -*-
""" user """
import datetime
import urllib, hashlib

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
    email = Field(data_type=unicode, index='email-index')
    hue = Field(data_type=int)
    status = Field(data_type='UserStatus')

    def __init__(self, *args, **kwargs):
        _kwargs = dict(
            status=UserStatus.ENABLED,
        )
        _kwargs.update(kwargs)
        super(User, self).__init__(*args, **_kwargs)

    def get_avatar_url(self, size):
        return "http://www.gravatar.com/avatar/{}?s={:d}".format(
            hashlib.md5(self.email.lower()).hexdigest(), size)

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "hue": self.hue,
            "status": self.status.value,
        }


class UserCredential(Model):
    u""" user credential model """
    user_id = Field(data_type='identity', hash_key=True)
    credential_type = Field(data_type='CredentialType', index='credentail-type-index')
    key = Field(data_type=str)
    secret = Field(data_type=str)
    created = Field(data_type=datetime.datetime, range_key=True)

    def __init__(self, *args, **kwargs):
        _kwargs = dict(
            created=datetime.datetime.utcnow(),
        )
        _kwargs.update(kwargs)
        super(UserCredential, self).__init__(*args, **_kwargs)
