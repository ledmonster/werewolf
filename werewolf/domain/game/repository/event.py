# -*- coding: utf-8 -*-
from werewolf.domain.game.models import *


class EventRepository(object):
    u""" イベントに関する処理を行う Repository """
    def __init__(self, engine):
        self.engine = engine

    def get_current_events(self, village):
        u""" TODO: order について確認 """
        generation = village.generation
        return self.engine.scan(EventModel).filter(
            village_id=village.identity,
            generation=village.generation,
        ).all()

    def add(self, entity):
        if not isinstance(entity, EternalEvent):
            raise ValueError("entity is not an EternalEvent")
        self.engine.save(entity.to_model())
