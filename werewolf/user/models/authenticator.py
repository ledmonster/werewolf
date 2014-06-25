""" auth (using Google Backend) """
import random

from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError

from werewolf import settings
from werewolf.util import Util
from werewolf.user.models import *
from werewolf.exception import *



class Authenticator(object):
    """ Authenticator """

    def __init__(self, client_id):
        if settings.OAUTH2["CLIENT_ID"] != client_id:
            raise InvalidClientError('Invalid client_id: {}'.format(client_id))


class IdTokenAuthenticator(Authenticator):
    """ ID Token Authenticator """

    def validate(self, assertion):
        """ validate assertion and return client session """
        if isinstance(assertion, unicode):
            assertion = assertion.encode('ascii')

        try:
            audience = settings.OAUTH2["CLIENT_ID"]
            payload = verify_id_token(assertion, audience)
        except AppIdentityError:
            raise InvalidGrantError('Invalid id_token: {}'.format(assertion))

        try:
            credential = UserCredential.objects.get(
                credential_type=CredentialType.GOOGLE,
                key=payload['sub'])
            user = credential.user
        except UserCredential.DoesNotExist:
            params = dict()
            if 'email' in payload.keys():
                params['email'] = payload['email']
                params['name'] = payload['email'].split('@')[0]
                params['hue'] = int(random.random() * 360)
            try:
                if params.get('email'):
                    user = User.objects.get(email=params['email'])
            except User.DoesNotExist:
                user = User.objects.create(**params)

            UserCredential.objects.create(
                user=user,
                credential_type=CredentialType.GOOGLE,
                key=payload['sub'])

        return ClientSession.objects.create(user=user)


class RefreshTokenAuthenticator(Authenticator):
    """ Refresh Token Authenticator """

    def validate(self, refresh_token):
        """ validate refresh_token and return client session """
        raise NotImplementedError()
