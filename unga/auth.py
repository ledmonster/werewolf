""" auth """

from unga.models import ClientSession, Client, User


class Authenticator(object):
    """ Authenticator """

    def __init__(self, client_id):
        # TODO: validate client_id
        self.client = Client(client_id)


class IdTokenAuthenticator(Authenticator):
    """ ID Token Authenticator """

    def validate(self, assertion):
        """ validate assertion and return client session """
        # TODO: validate assertion

        # TODO: get or create user from client and assertion
        user = User.create('1')

        return ClientSession.create(user, self.client)


class RefreshTokenAuthenticator(Authenticator):
    """ Refresh Token Authenticator """

    def validate(self, refresh_token):
        """ validate refresh_token and return client session """
        # TODO: get refresh_token object, and check expire

        # TODO: get client session assigned to refresh token
        user = User.create('1')

        return ClientSession.create(user, self.client)
