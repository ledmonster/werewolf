""" client session """
import datetime
import uuid


class ClientSession(object):
    """ Client Session """

    def __init__(self, identity, user, client):
        self.identity = identity
        self.user = user
        self.client = client

    @classmethod
    def create(cls, user, client):
        return cls(uuid.uuid1(), user, client)

    def generate_access_token(self):
        return AccessToken.create(self)

    def generate_refresh_token(self):
        return RefreshToken.create(self)


class AccessToken(object):
    """ access token """

    EXPIRES_IN = 3600

    def __init__(self, client_session, token, expires_at):
        self.client_session = client_session
        self.token = token
        self.expires_at = expires_at

    @classmethod
    def create(cls, client_session):
        token = generate_token()
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=cls.EXPIRES_IN)
        return cls(client_session, token, expires_at)


class RefreshToken(object):
    """ refresh token """

    EXPIRES_IN = 3600 * 24 * 365  # 1 year

    def __init__(self, client_session, token, expires_at):
        self.client_session = client_session
        self.token = token
        self.expires_at = expires_at

    @classmethod
    def create(cls, client_session):
        token = generate_token()
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=cls.EXPIRES_IN)
        return cls(client_session, token, expires_at)


def generate_token():
    import random, string
    return ''.join(random.SystemRandom('unga').choice(
        string.ascii_letters + string.digits) for x in range(32))
