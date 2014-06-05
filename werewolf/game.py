# -*- encoding: utf-8 -*-
""" Kind of domain layer in this application. 
Game class aggregates objects behind this game. """

from werewolf.models import *
from werewolf.util import Util


MEMBER_TYPES = {
    3: [
        [Role.WOLF, Role.BERSERKER, Role.VILLAGER],
        [Role.WOLF, Role.HUNTER, Role.VILLAGER],
    ],
}

class Game(object):

    instances = {}

    def get_instance(cls, village_id):
        if village_id not in cls.instances:
            cls.instances[village_id] = cls(village_id)
        return cls.instances[village_id]

    def __init__(self, village_id):
        self.village_id = village_id
        village = Village.objects.get(identity=village_id)
        self.village = village

    def start(self):
        self.assign_roles(self.residents)
        self.announce_roles(self.residents)
        
    def add_resident(self, user):
        resident, created = Resident.objects.get_or_create(
            village=self.village, user=user, role=None)
        return (resident, created)

    def assign_roles(self, residents):
        if len(residents) < 3:
            raise ValueError("Too few residents")
        elif len(residents) > 3:
            raise ValueError("Too many residents")
        roles = Util.shuffle(random.choice(MEMBER_TYPES[3]))
        for i, resident in enumerate(residents):
            resident.role = roles[i].value
            resident.save()

    def announce_roles(self, residents):
        pass
