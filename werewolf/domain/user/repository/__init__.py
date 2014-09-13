# -*- coding: utf-8 -*-

from .user import UserRepository, UserCredentialRepository
from .auth import (
    AccessTokenRepository,
    RefreshTokenRepository,
    ClientSessionRepository
)


__REPOS = {}
__SUPPORTED_KEYS = [
    "user",
    "user_credential",
    "access_token",
    "refresh_token",
    "client_session",
]


def register_repository(key, repo):
    if key not in __SUPPORTED_KEYS:
        raise ValueError
    __REPOS[key] = repo


def get_repository(key):
    return __REPOS.get(key)
