# -*- coding: utf-8 -*-
from werewolf.domain.event import *
from werewolf.models import *
from .village import VillageRepository


class EventRepository(object):
    u""" イベントに関する処理を行う Repository """
    def __init__(self, village_id):
        self.village_id = village_id
        self.village_repository = VillageRepository(village_id)

    def get_current_events(self):
        village = self.village_repository.get_entity()
        generation = village.generation
        return EventModel.objects.filter(
            village_id=self.village_id,
            generation=generation).order_by('created').all()

    def add(self, entity):
        if not isinstance(entity, EternalEvent):
            raise ValueError("entity is not an EternalEvent")
        entity.to_model().save()
