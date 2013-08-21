""" auth """

from unga.models import ClientSession, Client, User


class Authenticator(object):
    """ Authenticator """
    def __init__(self, client_id):
        # TODO: validate client_id
        self.client = Client(client_id)

    def validate(self, assertion):
        """ validate assertion and return client session """
        # TODO: validate assertion

        # TODO: get or create user from client and assertion
        user = User.create('1')

        return ClientSession.create(user, self.client)
