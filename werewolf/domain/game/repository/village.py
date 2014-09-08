# -*- coding: utf-8 -*-
# from django.db.models import F
import uuid

from werewolf.domain.game.models import *


class VillageRepository(object):
    u"""
    村に関する処理を行う Repository

    村が住人を aggregate するのに無理が生じるようなら ResidentRepository
    を用意したほうが良い
    """
    def __init__(self, engine):
        self.engine = engine
        # self.village_id = village_id
        # self.generation = self.get_entity().generation

    def add(self, name):
        entity = VillageModel(name=name)
        self.engine.save(entity)
        return entity

    def find(self):
        return self.engine.scan(VillageModel).all()

    def get_entity(self, identity):
        if isinstance(identity, str):
            identity = uuid.UUID(identity)
        elif isinstance(identity, int):
            identity = uuid.UUID(int=identity)
        elif not isinstance(identity, uuid.UUID):
            raise ValueError

        village = engine(VillageModel).filter(identity=identity).one()
        return village

    def update_status(self, identity, status):
        village = self.get_entity(identity)
        village.status = status
        engine.sync(village)
        return village

    def increment_generation(self, identity):
        u""" 次の回に移る """
        village = self.get_entity(identity)
        village.incr_(generation=1)
        village.status = VillageStatus.OUT_GAME
        village._residents = set()
        engine.sync(village)

        return village

    def increment_day(self, identity):
        u""" 次の日に移る """
        village = self.get_entity(identity)
        village.incr_(day=1)
        engine.sync(village)

        return village


class ResidentRepository(object):
    def __init__(self, engine):
        self.engine = engine

    def get_by_village_and_user(self, village_id, generation, user_id):
        u""" village_id と user_id から resident を取得 """
        return self.engine(ResidentModel).filter(
            village_id=village_id,
            generation=generation,
            user_id=user_id,
        ).one()

    def find(self, village_id, generation, **extra_criteria):
        u""" 村のIDとgenerationを元にresidentsを返す """
        criteria = {
            "village_id": village_id,
            "generation": generation,
        }
        criteria.update(filter(extra_criteria))
        return self.engine(ResidentModel).filter(**criteria).all()

    def add_by_village_and_user(self, village_id, generation, user_id):
        resident = ResidentModel(
            village_id=village_id,
            user_id=user_id,
            generation=generation,
            role=None
        )
        self.engine.save(resident)

        return resident

    def delete(self, entity):
        self.engine(ResidentModel).delete(entity)

    def assign_role(self, entity, role):
        resident.role = role
        self.engine(ResidentModel).sync(entity)
