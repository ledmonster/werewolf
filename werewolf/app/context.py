# -*- coding: utf-8 -*-
from pyramid.security import Allow, Everyone, Authenticated


class RootFactory(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, 'everyone'),
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        pass
