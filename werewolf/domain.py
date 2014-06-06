# -*- encoding: utf-8 -*-
""" Kind of domain layer in this application.
Game class aggregates objects behind this game. """

import random
from werewolf.exception import GameException, GameNotFinished
from werewolf.models import *
from werewolf.util import Util


MEMBER_TYPES = {
    1: [
        [Role.VILLAGER],
        [Role.WOLF],
    ],
    2: [
        [Role.VILLAGER, Role.VILLAGER],
        [Role.WOLF, Role.VILLAGER],
    ],
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

    @classmethod
    def get_instance(cls, village_id):
        if village_id not in cls.instances:
            cls.instances[village_id] = cls(village_id)
        return cls.instances[village_id]

    def __init__(self, village_id):
        self.village_id = village_id
        village = Village.objects.get(identity=village_id)
        self.village = village

    def get_village(self):
        return self.village

    def in_game(self):
        return self.village.status == VillageStatus.IN_GAME

    def start(self):
        if self.in_game():
            raise GameException(u"既にゲームは始まっています")
        residents = self.assign_roles(self.get_residents())
        village = self.update_village_status(VillageStatus.IN_GAME)
        return village

    def satisfy_game_end(self):
        try:
            self.get_winner()
            return True
        except GameNotFinished as e:
            return False

    def get_winner(self):
        residents = self.get_alive_residents()
        wolves = [r for r in residents if r.role == Role.WOLF]
        humans = [r for r in residents if r.role != Role.WOLF]
        if len(wolves) == 0:
            return Winner(Winner.HUMAN)
        elif len(wolves) >= len(humans):
            return Winner(Winner.WOLF)
        raise GameNotFinished(u"まだゲームは終わっていません")

    def go_to_next_game(self):
        u""" generation を increment して次のゲームを始める """
        if not self.in_game():
            raise GameException(u"ゲームは始まっていません")
        village = self.increment_generation()
        return village

    def increment_generation(self):
        u""" 次の回に移る """
        self.village.generation = self.village.generation + 1
        self.village.status = VillageStatus.OUT_GAME
        self.village.save()
        return self.village

    def increment_day(self):
        u""" 次の日に移る """
        self.village.day = self.village.day + 1
        self.village.save()
        return self.village

    def update_village_status(self, status):
        self.village.status = status
        self.village.save()
        return self.village

    def get_residents(self, role=None):
        if role:
            return Resident.objects.filter(
                village=self.village, generation=self.village.generation,
                role=role).all()
        return Resident.objects.filter(
            village=self.village, generation=self.village.generation).all()

    def get_alive_residents(self, role=None):
        if role:
            return Resident.objects.filter(
                village=self.village, generation=self.village.generation,
                status=ResidentStatus.ALIVE, role=role).all()
        return Resident.objects.filter(
            village=self.village, generation=self.village.generation,
            status=ResidentStatus.ALIVE).all()

    def get_resident(self, user):
        try:
            return Resident.objects.get(
                village=self.village, user=user, generation=self.village.generation)
        except Resident.DoesNotExist:
            raise GameException(u"%sさんは村に参加していません" % user.name)

    def add_resident(self, user):
        if self.in_game():
            raise GameException(u"ゲームの開催中は参加できません")
        try:
            resident = Resident.objects.get(
                village=self.village, user=user, generation=self.village.generation, role=None)
            raise GameException(u"%s さんは既に村に参加しています" % user.name)
        except Resident.DoesNotExist as e:
            resident = Resident.objects.create(
                village=self.village, user=user, generation=self.village.generation, role=None)
        return resident

    def remove_resident(self, resident):
        resident.delete()

    def get_role_constitution(self):
        if not self.in_game():
            raise GameException(u"まだゲームは始まっていません")
        residents = self.get_residents()
        roles = [r.role for r in residents]
        return [Role(r) for r in sorted(roles)]

    def assign_roles(self, residents):
        num_residents = len(residents)
        if num_residents < 1:
            raise GameException(u"住人が少なすぎます")
        elif num_residents > 6:
            raise GameException(u"住人が多すぎます")
        roles = Util.shuffle(random.choice(MEMBER_TYPES[num_residents]))
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
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を吊り対象にすることはできません")
        self.create_or_update_behavior(
            BehaviorType.EXECUTION, resident, target_resident)

    def set_attack_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role != Role.WOLF:
            raise GameException(u"あなたは狼ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を襲撃することはできません")
        if target_resident.role == Role.WOLF:
            raise GameException(u"仲間を襲撃することはできません")
        self.create_or_update_behavior(
            BehaviorType.ATTACK, resident, target_resident)

    def set_hunt_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role != Role.HUNTER:
            raise GameException(u"あなたは狩人ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を道連れにすることはできません")
        self.create_or_update_behavior(
            BehaviorType.HUNT, resident, target_resident)

    def set_fortune_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role != Role.TELLER:
            raise GameException(u"あなたは占い師ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を占うことはできません")
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
        if not self.in_game():
            raise GameException(u"まだゲームは始まってません")
        try:
            resident = Resident.objects.get(
                village=self.village, user=user, generation=self.village.generation)
        except Resident.DoesNotExist:
            raise GameException(u"%s さんは村の住人ではありません" % user.name)
        if resident.status != ResidentStatus.ALIVE:
            raise GameException(u"%s さんは既に死んでいます" % user.name)
        return resident

    def execute_night(self):
        u"""
        - 吊り対象を決めて吊る
        - 襲撃対象を決めて襲撃する
        - 道連れ対象を決めて道連れにする
        - 占い対象を決めて結果を知らせる
        """

        if not self.in_game():
            raise GameException(u"ゲームは開始されていません")

        targets = {}

        # 占い
        residents = self.get_alive_residents()
        targets['fortune'] = self.select_fortune_target(residents)

        # 吊り
        targets['execution'] = self.select_execution_target(residents)
        if targets['execution']:
            residents = self.kill_resident(targets['execution'])
            if targets['execution'].role == Role.HUNTER:
                targets['hunt'] = self.select_hunt_target(hunter, residents)
                residents = self.kill_resident(targets['hunt'])

        # 襲撃
        targets['attack'] = self.select_attack_target(residents)
        if targets['attack']:
            residents = self.kill_resident(targets['attack'])
            if targets['execution'].role == Role.HUNTER:
                targets['hunt'] = self.select_hunt_target(hunter, residents)
                residents = self.kill_resident(targets['hunt'])

        return targets

    def kill_resident(self, resident):
        u""" 住民が死ぬ """
        resident.status = ResidentStatus.DEAD
        resident.save()
        return self.get_alive_residents()

    def select_execution_target(self, residents):
        u""" 吊り対象を選ぶ """
        return self.select_action_target(BehaviorType.EXECUTION, residents, residents)

    def select_attack_target(self, residents):
        humans = [r for r in residents if r.role != Role.WOLF]
        wolves = [r for r in residents if r.role == Role.WOLF]
        return self.select_action_target(BehaviorType.ATTACK, wolves, humans)

    def select_hunt_target(self, hunter, residents):
        target = self.select_action_target(BehaviorType.HUNT, [hunter], residents)
        self.kill_resident(target)

    def select_fortune_target(self, residents):
        tellers = [r for r in residents if r.role == Role.TELLER]
        target = self.select_action_target(BehaviorType.FORTUNE, tellers, residents)
        return target

    def select_action_target(self, behavior_type, executors, targets):
        voted = []
        for r in executors:
            try:
                behavior = Behavior.objects.get(
                    behavior_type=behavior_type,
                    village=self.village,
                    generation=self.village.generation,
                    day=self.village.day,
                    resident=r)
                voted.append(behavior.target_resident)
            except Behavior.DoesNotExist:
                # ランダム選択. ここのロジックは Model に __eq__ が定義されてるからできる
                targets = [rr for rr in targets if rr != r]
                if targets:
                    voted.append(Util.shuffle(targets)[0])
        return Util.select_most_voted(voted)

    def send_message(self, user, message):
        u"""
        ゲーム開始状態でなければ誰でもメッセージを送れるが、
        ゲーム開始状態の場合は生きている参加者しかメッセージを送れない。
        """
        if self.in_game():
            self.ensure_alive_resident(user)
        self.save_event(EventType.MESSAGE, user, {"message": message})
        return message

    def save_event(self, event_type, user, content):
        return Event.objects.create(
            event_type=event_type,
            user=user,
            village=self.village,
            generation=self.village.generation,
            content=content);
