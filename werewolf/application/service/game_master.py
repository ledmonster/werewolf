# -*- coding: utf-8 -*-
""" game master service on application layer, which manages games'
 time scheduling or so on. """

import logging
import random
import threading

from werewolf.models import *

logger = logging.getLogger()

class ResidentManager(object):

    EVENT_RESIDENT_ADDED = 1
    EVENT_RESIDENT_REMOVED = 2

    def __init__(self):
        self.listeners = {
            self.EVENT_RESIDENT_ADDED: [],
            self.EVENT_RESIDENT_REMOVED: []}

    def register(self, event_type, listener):
        self.listeners[event_type].append(listener)

    def unregister(self, event_type, listener):
        self.listeners[event_type].remove(listener)

    def add_resident(self, village, user):
        resident, created = ResidentModel.objects.get_or_create(village=village, user=user)
        if created:
            for listener in self.listeners[self.EVENT_RESIDENT_ADDED]:
                listener(village, resident)

    def remove_resident(self, village, user):
        raise NotImplementedError


class GameMaster(object):
    """ Game master
    Game master manages game, villages and residents.
    """

    def __init__(self, messenger, resident_manager):
        self.messenger = messenger
        self.resident_manager = resident_manager
        self.resident_manager.register(
            ResidentManager.EVENT_RESIDENT_ADDED, self.on_resident_added)

    def on_resident_added(self, village, resident):
        """ callback method for resident added """
        logger.info("on resident added")
        num_roles = len(village.ROLES)
        num_residents = village.residentmodel_set.count()
        if num_residents == num_roles:
            self.start_game(village)

    def start_prologue(self, village):
        """ Start prologue """
        logger.info("start prologue")
        village.update_status(VillageModel.STATUS_PROLOGUE)
        village.save()
        self.messenger.send_gm_message(village, u"おはよう。今日も良い一日になるといいな。")

    def start_game(self, village):
        """ Start game with residents. Assign a role to each resident here. """
        logger.info("start game")
        self._assign_roles(village)
        village.update_status(VillageModel.STATUS_IN_GAME)
        village.save()

        # TODO: 各 Resident に Role を送信

        messages = [
            u"朝起きると、村長の無残な姿が見つかりました。",
            u"この村に狼が紛れ込んでいるようです。"]
        self.start_daytime(village, messages)

    def start_daytime(self, village, morning_messages=None):
        """ Start daytime for discussion """
        logger.info("start daytime")
        village.increment_day()
        village.save()

        timer = threading.Timer(village.DAYTIME_LENGTH, self.start_night, [village])
        timer.start()

        if morning_messages:
            for message in morning_messages:
                self.messenger.send_gm_message(village, message)

    def start_night(self, village):
        """ Start night for event execution """
        logger.info("start night")
        # TODO: 夜間処理
        messages = []

        # execution
        execution_target = self._select_execution_target(village)
        execution_target.update_status(ResidentModel.STATUS_EXECUTED)
        execution_target.save()
        messages.append(u"{} が吊られました。".format(execution_target.user.name))

        # TODO: fortne telling
        fortune_telling_target = self._select_fortune_telling_target(village)

        # attack from werewolf
        attack_target = self._select_attack_target(village)
        if attack_target:
            attack_target.update_status(ResidentModel.STATUS_ATTACKED)
            attack_target.save()
            messages.append(u"{} が狼に襲撃されました。".format(attack_target.user.name))
        else:
            messages.append(u"誰も狼に襲撃されませんでした。")

        # TODO: check game end status
        num_residents = ResidentModel.objects.filter(
            village=village, status=ResidentModel.STATUS_ALIVE).count()
        num_wolves = ResidentModel.objects.filter(
            village=village, status=ResidentModel.STATUS_ALIVE,
            role=ResidentModel.ROLE_WOLF).count()
        if num_wolves == 0:
            game_finished = True
        elif num_wolves * 2 >= num_residents:
            game_finished = True
        else:
            game_finished = False

        if game_finished:
            self.start_epilogue(village, messages)
        else:
            self.start_daytime(village, messages)

    def _select_fortune_telling_target(self, village):
        behaviors = BehaviorModel.objects.filter(
            village=village, day=village.day, behavior_type=BehaviorModel.TYPE_FORTUNE_TELLING)
        if behaviors:
            return behaviors.pop()

    def _select_execution_target(self, village):
        behaviors = BehaviorModel.objects.filter(
            village=village, day=village.day, behavior_type=BehaviorModel.TYPE_EXECUTION)
        target_residents = [behavior.target_resident for behavior in behaviors]
        if not target_residents:
            target_residents = village.residentmodel_set.filter(status=ResidentModel.STATUS_ALIVE)
        return self._select_by_election(target_residents)

    def _select_attack_target(self, village):
        behaviors = BehaviorModel.objects.filter(
            village=village, day=village.day, behavior_type=BehaviorModel.TYPE_ATTACK)
        target_residents = [behavior.target_resident for behavior in behaviors]
        if not target_residents:
            target_residents = village.residentmodel_set.\
                filter(status=ResidentModel.STATUS_ALIVE).\
                exclude(role=ResidentModel.ROLE_WOLF)
        return self._select_by_election(target_residents)

    def _select_by_election(self, items):
        """ TODO: move to infrastructure layer """
        votes = dict()
        for item in items:
            votes[item] = votes.setdefault(item, 0) + 1
        max_votes = max(votes.values())
        candidates = [item for item in set(items) if votes[item] == max_votes]
        return random.choice(candidates)

    def start_epilogue(self, village, morning_messages=None):
        """ Start epilogue for reviewing a game """
        logger.info("start epilogue")
        village.update_status(VillageModel.STATUS_EPILOGUE)
        village.save()

        timer = threading.Timer(village.DAYTIME_LENGTH, self.end_epilogue, [village])
        timer.start()

        if morning_messages:
            for message in morning_messages:
                self.messenger.send_gm_message(village, message)

    def end_epilogue(self, village):
        """ End epilogue, finish reviewing """
        logger.info("end epilogue")
        # TODO: MVP を決めてメッセージを流すなど
        village.update_status(VillageModel.STATUS_CLOSED)
        village.save()

    def _assign_roles(self, village):
        roles = random.sample(village.ROLES, len(village.ROLES))
        residents = village.residentmodel_set.all()
        if len(residents) != len(roles):
            raise RuntimeError
        for resident in residents:
            resident.role = roles.pop()
            resident.save()
