# -*- coding: utf-8 -*-
from werewolf.domain.game.models import *
from .village import VillageRepository


class BehaviorRepository(object):
    u"""
    ユーザ操作に関する処理を行う Repository
    """
    def __init__(self, engine):
        self.engine = engine
        self.village_repository = VillageRepository(village_id)

    def create_or_update(self, village_id, generation, day, behavior_type,
                         resident_id, target_resident_id):
        village = self.village_repository.get_entity()
        try:
            behavior = self.get_by_type_and_resident(
                village_id,
                generation,
                day,
                behavior_type,
                resident_id
            )
            behavior.target_resident_id = target_resident_id
            self.engine.sync(behavior)
        except ValueError:
            behavior = BehaviorModel(
                behavior_type=behavior_type,
                village_id=village_id,
                resident_id=resident_id,
                target_resident_id=target_resident_id,
                generation=generation,
                day=day)
            self.engine.save(behavior)
        return behavior

    def get_by_type_and_resident(self, village_id, generation, day,
                                 behavior_type, resident_id):
        return self.engine(BehaviorModel).filter(
            behavior_type=behavior_type,
            village_id=village_id,
            generation=generation,
            day=day,
            resident_id=resident_id
        ).one()
