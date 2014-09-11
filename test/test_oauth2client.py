# -*- coding: utf-8 -*-
import os

from werewolf import settings
from werewolf.auth import IdTokenAuthenticator


class TestIdTokenAuthenticator(object):

    def test_validate(self):
        client_id = settings.OAUTH2["CLIENT_ID"]
        id_token = self.get_id_token()
        authenticator = IdTokenAuthenticator(client_id)
        authenticator.validate(id_token)

    def test_validate_with_unicode_id_token(self):
        client_id = settings.OAUTH2["CLIENT_ID"]
        id_token = unicode(self.get_id_token())
        authenticator = IdTokenAuthenticator(client_id)
        authenticator.validate(id_token)

    def get_id_token(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".id_token")
        with open(path) as fp:
            id_token = fp.read()
        return id_token
