# -*- coding: utf-8 -*-
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

    def add(self, name):
        entity = VillageModel(name=name)
        self.engine.save(entity)
        return entity

    def find(self):
        return self.engine.scan(VillageModel).all()

    def get_entity(self, identity):
        if isinstance(identity, basestring):
            identity = uuid.UUID(hex=identity)
        elif isinstance(identity, int):
            identity = uuid.UUID(int=identity)
        elif not isinstance(identity, uuid.UUID):
            raise ValueError

        village = self.engine(VillageModel).filter(identity=identity).one()
        return village

    def update_status(self, identity, status):
        village = self.get_entity(identity)
        village.status = status
        self.engine.sync(village)
        return village

    def increment_generation(self, identity):
        u""" 次の回に移る """
        village = self.get_entity(identity)
        village.incr_(generation=1)
        village.status = VillageStatus.OUT_GAME
        village._residents = set()
        self.engine.sync(village)

        return village

    def increment_day(self, identity):
        u""" 次の日に移る """
        village = self.get_entity(identity)
        village.incr_(day=1)
        self.engine.sync(village)

        return village


class ResidentRepository(object):
    def __init__(self, engine):
        self.engine = engine

    def get_by_village_and_user(self, village_id, generation, user_id):
        u""" village_id と user_id から resident を取得 """
        return self.engine.scan(ResidentModel).filter(
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
        criteria.update(extra_criteria)
        criteria = dict([(k, v) for k, v in criteria.iteritems() if v is not None])
        return self.engine.scan(ResidentModel).filter(**criteria).all()

    def add_by_village_and_user(self, village, user):
        resident = ResidentModel(
            name=user.name,
            village_id=village.identity,
            user_id=user.identity,
            generation=village.generation,
            role=None
        )
        self.engine.save(resident)

        return resident

    def delete(self, entity):
        self.engine(ResidentModel).delete(entity)

    def assign_role(self, entity, role):
        entity.role = role
        self.engine.sync(entity)

    def update_status(self, entity, status):
        entity.status = status
        self.engine.sync(entity)
        return entity
