""" auth (using Google Backend) """

from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError

from werewolf import settings
from werewolf.models import ClientSession, User
from werewolf.exception import *



class Authenticator(object):
    """ Authenticator """

    def __init__(self, client_id):
        if settings.OAUTH2["CLIENT_ID"] != client_id:
            raise InvalidClientError('Invalid client_id: %s' % client_id)


class IdTokenAuthenticator(Authenticator):
    """ ID Token Authenticator """

    def validate(self, assertion):
        """ validate assertion and return client session """
        try:
            audience = settings.OAUTH2["CLIENT_ID"]
            payload = verify_id_token(assertion, audience)
        except AppIdentityError:
            raise InvalidGrantError('Invalid id_token: %s' % assertion)

        user, created = User.objects.get_or_create(identity=payload['sub'])
        return ClientSession.objects.create(user=user)


class RefreshTokenAuthenticator(Authenticator):
    """ Refresh Token Authenticator """

    def validate(self, refresh_token):
        """ validate refresh_token and return client session """
        raise NotImplementedError()
