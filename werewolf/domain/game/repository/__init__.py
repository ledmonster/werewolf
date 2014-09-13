# -*- coding: utf-8 -*-

from .village import VillageRepository, ResidentRepository
from .event import EventRepository
from .behavior import BehaviorRepository


__REPOS = {}
__SUPPORTED_KEYS = [
    "village",
    "resident",
    "event",
    "behavior",
]


def register_repository(key, repo):
    if key not in __SUPPORTED_KEYS:
        raise ValueError
    __REPOS[key] = repo


def get_repository(key):
    return __REPOS.get(key)
