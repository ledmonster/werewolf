# -*- coding: utf-8 -*-
from django.db.models import F

from werewolf.models import *


class VillageRepository(object):
    u"""
    村に関する処理を行う Repository
    Note: Repository なら村単体に紐付けるべきでないかも。
    """
    def __init__(self, village_id):
        self.village_id = village_id
        self.generation = self.get_entity().generation

    def get_entity(self):
        return VillageModel.objects.get(identity=self.village_id)

    def update_status(self, status):
        village = self.get_entity()
        village.status = status
        village.save()
        return village

    def increment_generation(self):
        u""" 次の回に移る """
        village = self.get_entity()
        village.generation = F('generation') + 1
        village.status = VillageStatus.OUT_GAME
        village.save()

        # entity updated by F method should be reloaded
        new_village = self.get_entity()
        self.generation = new_village.generation
        return new_village

    def increment_day(self):
        u""" 次の日に移る """
        village = self.get_entity()
        village.day = F('day') + 1
        village.save()

        # entity updated by F method should be reloaded
        new_village = self.get_entity()

        return new_village

    def get_residents(self, role=None):
        if role:
            return ResidentModel.objects.filter(
                village_id=self.village_id, generation=self.generation,
                role=role).all()
        return ResidentModel.objects.filter(
            village_id=self.village_id, generation=self.generation).all()

    def get_alive_residents(self, role=None):
        if role:
            return ResidentModel.objects.filter(
                village_id=self.village_id, generation=self.generation,
                status=ResidentStatus.ALIVE, role=role).all()
        return ResidentModel.objects.filter(
            village_id=self.village_id, generation=self.generation,
            status=ResidentStatus.ALIVE).all()

    def add_resident(self, user):
        return ResidentModel.objects.create(
            village_id=self.village_id, user=user, generation=self.generation, role=None)

    def get_resident(self, user):
        return ResidentModel.objects.get(
            village_id=self.village_id, user=user, generation=self.generation)
