""" application and client """
import uuid


class Application(object):
    """ Application """
    pass


class Client(object):
    """ Client """
    def __init__(self, identity):
        if isinstance(identity, str):
            identity = uuid.UUID(identity)
        self.identity = identity
