""" auth (using Google Backend) """
import random

from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError

from werewolf.domain.user.models import *
from werewolf.domain.user.exception import *


class Authenticator(object):
    """ Authenticator """

    def __init__(self, context, client_id):
        self.context = context
        self.client_id = client_id


class IdTokenAuthenticator(Authenticator):
    """ ID Token Authenticator """

    def validate(self, assertion):
        """ validate assertion and return client session """
        if isinstance(assertion, unicode):
            assertion = assertion.encode('ascii')

        try:
            audience = self.client_id
            payload = verify_id_token(assertion, audience)
        except AppIdentityError:
            raise InvalidGrantError('Invalid id_token: {}'.format(assertion))

        repo_user = self.context.repos['user']
        repo_credential = self.context.repos['user_credential']
        repo_session = self.context.repos['client_session']

        try:
            credential = repo_credential.get(
                credential_type=CredentialType.GOOGLE,
                key=payload['sub'])
            user_id = credential.user_id
        except ValueError:
            params = dict()
            if 'email' in payload.keys():
                params['email'] = payload['email']
                params['name'] = payload['email'].split('@')[0]
                params['hue'] = int(random.random() * 360)
            try:
                if params.get('email'):
                    user = repo_user.get_by_email(params['email'])
            except ValueError:
                user = repo_user.create(**params)

            user_id = user.identity
            repo_credential.create(
                user_id=user_id,
                credential_type=CredentialType.GOOGLE,
                key=payload['sub'])

        return repo_session.create(user_id=user_id)


class RefreshTokenAuthenticator(Authenticator):
    """ Refresh Token Authenticator """

    def validate(self, refresh_token):
        """ validate refresh_token and return client session """
        raise NotImplementedError()
