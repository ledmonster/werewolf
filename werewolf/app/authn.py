# -*- coding: utf-8 -*-
import logging

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPUnauthorized
from zope.interface import implementer

from werewolf.domain.user.models import AccessToken

logger = logging.getLogger(__name__)


# braught from pyramid_oauth2_provider, and modified
@implementer(IAuthenticationPolicy)
class OAuth2AuthenticationPolicy(CallbackAuthenticationPolicy):
    u""" OAuth2 用の認証ポリシー

    pyramid_oauth2_provider package の OauthAuthenticationPolicy を改変
    """

    def _get_auth_token(self, request):
        credentials = get_client_credentials(request)
        if not credentials:
            return None
        token_type, token = credentials
        if token_type != 'bearer':
            return None

        try:
            auth_token = AccessToken.objects.get(token=token)
        except AccessToken.DoesNotExist:
            # Bad input, return 400 Invalid Request
            raise HTTPBadRequest()

        # Expired or revoked token, return 401 invalid token
        if auth_token.is_revoked():
            raise HTTPUnauthorized()

        return auth_token

    def unauthenticated_userid(self, request):
        auth_token = self._get_auth_token(request)
        if not auth_token:
            return None

        return auth_token.client_session.user_id

    def remember(self, request, principal, **kw):
        """
        I don't think there is anything to do for an oauth request here.
        """

    def forget(self, request):
        auth_token = self._get_auth_token(request)
        if not auth_token:
            return None

        auth_token.revoke()


# braught from pyramid_oauth2_provider, and modified
def get_client_credentials(request):
    if 'Authorization' in request.headers:
        auth = request.headers.get('Authorization')
    elif 'authorization' in request.headers:
        auth = request.headers.get('authorization')
    else:
        logger.debug('no authorization header found')
        return False

    if (not auth.lower().startswith('bearer') and
        not auth.lower().startswith('basic')):
        logger.debug('authorization header not of type bearer or basic: %s'
            % auth.lower())
        return False

    parts = auth.split()
    if len(parts) != 2:
        return False

    token_type = parts[0].lower()
    token = parts[1]

    return token_type, token
