# -*- encoding: utf-8 -*-
""" Kind of domain layer in this application. 
Game class aggregates objects behind this game. """
import random
from werewolf.models import *
from werewolf.util import Util


MEMBER_TYPES = {
    3: [
        [Role.WOLF, Role.BERSERKER, Role.VILLAGER],
        [Role.WOLF, Role.HUNTER, Role.VILLAGER],
    ],
    4: [
        [Role.WOLF, Role.BERSERKER, Role.HUNTER, Role.VILLAGER],
    ],
    5: [
        [Role.WOLF, Role.BERSERKER, Role.TELLER, Role.HUNTER, Role.VILLAGER],
        [Role.WOLF, Role.BERSERKER, Role.TELLER, Role.VILLAGER, Role.VILLAGER],
    ],
    6: [
        [Role.WOLF, Role.BERSERKER, Role.TELLER, Role.HUNTER, Role.VILLAGER, Role.VILLAGER],
        [Role.WOLF, Role.BERSERKER, Role.TELLER, Role.VILLAGER, Role.VILLAGER, Role.VILLAGER],
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
        if self.village.status == VillageStatus.IN_GAME:
            raise Exception(u"既にゲームは始まっています")
        residents = self.assign_roles(self.village.resident_set.all())
        village = self.update_village_status(VillageStatus.IN_GAME)
        return village

    def update_village_status(self, status):
        village = Village.objects.get(identity=self.village.identity)
        village.status = status
        village.save()
        self.village = village
        return village

    def get_residents(self):
        return Resident.objects.filter(
            village=self.village, generation=self.village.generation).all()

    def get_resident(self, user):
        try:
            return Resident.objects.get(
                village=self.village, user=user)
        except Resident.DoesNotExist:
            return None
        
    def add_resident(self, user):
        resident, created = Resident.objects.get_or_create(
            village=self.village, user=user, generation=self.village.generation, role=None)
        return (resident, created)

    def remove_resident(self, resident):
        resident.delete()

    def assign_roles(self, residents):
        if len(residents) < 3:
            raise ValueError("Too few residents")
        elif len(residents) > 6:
            raise ValueError("Too many residents")
        roles = Util.shuffle(random.choice(MEMBER_TYPES[3]))
        for i, resident in enumerate(residents):
            resident.role = roles[i]
            resident.save()
        return residents

    def announce_roles(self, residents):
        pass
