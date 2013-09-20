""" auth """

from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError

from werewolf import settings
from werewolf.models import ClientSession, Client, User
from werewolf.exception import *



class Authenticator(object):
    """ Authenticator """

    def __init__(self, client_id):
        if settings.OAUTH2["CLIENT_ID"] != client_id:
            raise InvalidClientError('Invalid client_id: %s' % client_id)
        self.client = Client(client_id)


class IdTokenAuthenticator(Authenticator):
    """ ID Token Authenticator """

    def validate(self, assertion):
        """ validate assertion and return client session """
        try:
            audience = settings.OAUTH2["CLIENT_ID"]
            payload = verify_id_token(assertion, audience)
        except AppIdentityError:
            raise InvalidGrantError('Invalid id_token: %s' % assertion)

        user = User.create(payload['sub'])
        return ClientSession.create(user, self.client)


class RefreshTokenAuthenticator(Authenticator):
    """ Refresh Token Authenticator """

    def validate(self, refresh_token):
        """ validate refresh_token and return client session """
        # TODO: get refresh_token object, and check expire

        # TODO: get client session assigned to refresh token
        user = User.create('1')

        return ClientSession.create(user, self.client)
