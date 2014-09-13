# -*- coding: utf-8 -*-
from werewolf.domain.game.models import *
from .village import VillageRepository


class BehaviorRepository(object):
    u"""
    ユーザ操作に関する処理を行う Repository
    """
    def __init__(self, engine):
        self.engine = engine

    def create_or_update(self, village, behavior_type, resident_id,
                         target_resident_id):
        try:
            behavior = self.get_by_type_and_resident(
                village,
                behavior_type,
                resident_id
            )
            behavior.target_resident_id = target_resident_id
            self.engine.sync(behavior)
        except ValueError:
            behavior = BehaviorModel(
                behavior_type=behavior_type,
                village_id=village.identity,
                resident_id=resident_id,
                target_resident_id=target_resident_id,
                generation=village.generation,
                day=village.day)
            self.engine.save(behavior)
        return behavior

    def get_by_type_and_resident(self, village, behavior_type, resident_id):

        # TODO: flywheel のバグで scan と one() を組み合わせると正しい結果が返らない
        # ので all()[0] を使う
        try:
            return self.engine.scan(BehaviorModel).filter(
                behavior_type=behavior_type,
                village_id=village.identity,
                generation=village.generation,
                day=village.day,
                resident_id=resident_id
            ).all()[0]
        except IndexError:
            raise ValueError('behavior not found')
