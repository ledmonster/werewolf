""" client session """
import datetime
import uuid

from django.db import models
from uuidfield import UUIDField


def generate_token():
    import random, string
    return ''.join(random.SystemRandom('werewolf').choice(
        string.ascii_letters + string.digits) for x in range(32))


class ClientSession(models.Model):
    """ Client Session """
    identity = UUIDField(version=1, auto=True, primary_key=True)
    user = models.ForeignKey('User')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_access_token(self):
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=AccessToken.EXPIRES_IN)
        return AccessToken(client_session=self, expires_at=expires_at)

    def generate_refresh_token(self):
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=RefreshToken.EXPIRES_IN)
        return RefreshToken(client_session=self, expires_at=expires_at)

    class Meta:
        app_label = 'werewolf'


class AccessToken(models.Model):
    """ access token """
    EXPIRES_IN = 3600

    token = models.CharField(max_length=32, primary_key=True, default=generate_token)
    expires_at = models.DateTimeField()
    client_session = models.ForeignKey('ClientSession')

    class Meta:
        app_label = 'werewolf'


class RefreshToken(models.Model):
    """ refresh token """
    EXPIRES_IN = 3600 * 24 * 365  # 1 year

    token = models.CharField(max_length=32, primary_key=True, default=generate_token)
    expires_at = models.DateTimeField()
    client_session = models.ForeignKey('ClientSession')

    class Meta:
        app_label = 'werewolf'
