# -*- coding: utf-8 -*-
import datetime

from flywheel import Model, Field

from werewolf.domain.base import EntityModel, ValueObject


def generate_token():
    import random, string
    return ''.join(random.SystemRandom('werewolf').choice(
        string.ascii_letters + string.digits) for x in range(32))


class GrantType(ValueObject):
    JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    REFRESH_TOKEN = "refresh_token"


class ClientSession(EntityModel):
    u""" Client Session """
    user_id = Field(data_type='identity')

    def generate_access_token(self):
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=AccessToken.EXPIRES_IN_)
        return AccessToken(
            token=generate_token(),
            client_session_id=self.identity,
            expires_at=expires_at)

    def generate_refresh_token(self):
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=RefreshToken.EXPIRES_IN_)
        return RefreshToken(
            token=generate_token(),
            client_session_id=self.identity,
            expires_at=expires_at)


class AccessToken(Model):
    u""" Access Token """
    EXPIRES_IN_ = 3600 * 24

    token = Field(data_type=unicode, hash_key=True)
    expires_at = Field(data_type=datetime.datetime)
    client_session_id = Field(data_type='identity')

    def revoke(self):
        u""" TODO: Implement revoke """
        raise NotImplemented()

    def is_revoked(self):
        return self.expires_at < datetime.datetime.utcnow()


class RefreshToken(Model):
    u""" refresh token """
    EXPIRES_IN_ = 3600 * 24 * 365  # 1 year

    token = Field(data_type=unicode, hash_key=True)
    expires_at = Field(data_type=datetime.datetime)
    client_session_id = Field(data_type='identity')
