# -*- coding: utf-8 -*-
from werewolf.models import *
from .village import VillageRepository


class BehaviorRepository(object):
    u"""
    ユーザ操作に関する処理を行う Repository
    Note: Repository なら村単体に紐付けるべきでないかも
    """
    def __init__(self, village_id):
        self.village_id = village_id
        self.village_repository = VillageRepository(village_id)

    def create_or_update(self, behavior_type, resident, target_resident):
        village = self.village_repository.get_entity()
        try:
            behavior = BehaviorModel.objects.get(
                behavior_type=behavior_type, village=village,
                resident=resident, generation=village.generation,
                day=village.day)
            behavior.target_resident = target_resident
            behavior.save()
        except BehaviorModel.DoesNotExist:
            behavior = BehaviorModel.objects.create(
                behavior_type=behavior_type, village=village,
                resident=resident, target_resident=target_resident,
                generation=village.generation, day=village.day)
        return behavior

    def get_by_type_and_resident(self, behavior_type, resident):
        village = self.village_repository.get_entity()
        return BehaviorModel.objects.get(
            behavior_type=behavior_type,
            village=village,
            generation=village.generation,
            day=village.day,
            resident=resident)
