""" user """
import uuid


class User(object):
    """ user """
    def __init__(self, identity, ref_key=None):
        self.identity = identity
        self.ref_key = ref_key

    @classmethod
    def create(cls, ref_key):
        identity = uuid.uuid1()
        return cls(identity, ref_key)
