# -*- encoding: utf-8 -*-
""" Kind of domain layer in this application. 
Game class aggregates objects behind this game. """
import random
from werewolf.exception import GameException
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
    u"""
    ゲームロジックを書くクラス。
    """

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
            raise GameException(u"既にゲームは始まっています")
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
            raise GameException(u"さんは村に参加していません" % user.name)
        
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

    def create_or_update_behavior(self, behavior_type, resident, target_resident):
        try:
            behavior = Behavior.objects.get(
                behavior_type=behavior_type, village=self.village,
                resident=resident, generation=self.village.generation,
                day=self.village.day)
            behavior.target_resident = target_resident
            behavior.save()
        except Behavior.DoesNotExist:
            behavior = Behavior.objects.create(
                behavior_type=behavior_type, village=self.village,
                resident=resident, target_resident=target_resident,
                generation=self.village.generation, day=self.village.day)
        return behavior

    def set_execution_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        self.create_or_update_behavior(
            BehaviorType.EXECUTION, resident, target_resident)

    def set_attack_target(self, user, targert_name):
        resident = self.ensure_alive_resident(user)
        if resident.Role != Role.WOLF:
            raise GameException(u"あなたは狼ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        self.create_or_update_behavior(
            BehaviorType.ATTACK, resident, target_resident)

    def set_hunt_target(self, user, targert_name):
        resident = self.ensure_alive_resident(user)
        if resident.Role != Role.HUNTER:
            raise GameException(u"あなたは狩人ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        self.create_or_update_behavior(
            BehaviorType.HUNT, resident, target_resident)

    def set_fortune_target(self, user, targert_name):
        resident = self.ensure_alive_resident(user)
        if resident.Role != Role.TELLER:
            raise GameException(u"あなたは占い師ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        self.create_or_update_behavior(
            BehaviorType.FORTUNE, resident, target_resident)

    def get_user_by_name(self, name):
        u""" 名前をもとにユーザを取得(TODO: 同じ名前の人対応) """
        try:
            return User.objects.get(name=name)
        except:
            raise GameException(u"%s という名前の人はいません" % name)

    def ensure_alive_resident(self, user):
        u""" user がゲーム中の村の生きた住人であることを保障 """
        if self.village.status != VillageStatus.IN_GAME:
            raise GameException(u"まだゲームは始まってません")
        try:
            resident = Resident.objects.get(
                village=self.village, user=user)
        except Resident.DoesNotExist:
            raise GameException(u"%s さんは村の住人ではありません" % user.name)
        if resident.status != ResidentStatus.ALIVE:
            raise GameException(u"%s さんは既に死んでいます" % user.name)
        return resident
