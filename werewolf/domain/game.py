# -*- encoding: utf-8 -*-
""" Kind of domain layer in this application.
Game class aggregates objects behind this game. """

import random

from django.db.models import F

from werewolf.exception import GameException, GameNotFinished
from werewolf.domain.event import *
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


class VillageRepository(object):
    u"""
    村に関する処理を行う Repository
    Note: Repository なら村単体に紐付けるべきでないかも。
    """
    def __init__(self, village_id):
        self.village_id = village_id
        self.generation = self.get_entity().generation

    def get_entity(self):
        return VillageModel.objects.get(identity=self.village_id)

    def update_status(self, status):
        village = self.get_entity()
        village.status = status
        village.save()
        return village

    def increment_generation(self):
        u""" 次の回に移る """
        village = self.get_entity()
        village.generation = F('generation') + 1
        village.status = VillageStatus.OUT_GAME
        village.save()

        # entity updated by F method should be reloaded
        new_village = self.get_entity()
        self.generation = new_village.generation
        return new_village

    def increment_day(self):
        u""" 次の日に移る """
        village = self.get_entity()
        village.day = F('day') + 1
        village.save()

        # entity updated by F method should be reloaded
        new_village = self.get_entity()

        return new_village

    def get_residents(self, role=None):
        if role:
            return ResidentModel.objects.filter(
                village_id=self.village_id, generation=self.generation,
                role=role).all()
        return ResidentModel.objects.filter(
            village_id=self.village_id, generation=self.generation).all()

    def get_alive_residents(self, role=None):
        if role:
            return ResidentModel.objects.filter(
                village_id=self.village_id, generation=self.generation,
                status=ResidentStatus.ALIVE, role=role).all()
        return ResidentModel.objects.filter(
            village_id=self.village_id, generation=self.generation,
            status=ResidentStatus.ALIVE).all()

    def get_resident(self, user):
        return ResidentModel.objects.get(
            village_id=self.village_id, user=user, generation=self.generation)


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


class EventRepository(object):
    u""" イベントに関する処理を行う Repository """
    def __init__(self, village_id):
        self.village_id = village_id


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

        self.village_repository = VillageRepository(village_id)
        self.event_repository = EventRepository(village_id)
        self.behavior_repository = BehaviorRepository(village_id)

        self.village = self.village_repository.get_entity()

    def in_game(self):
        return self.village.status == VillageStatus.IN_GAME

    def start(self):
        if self.in_game():
            raise GameException(u"既にゲームは始まっています")
        residents = self.assign_roles(self.get_residents())
        self.village = self.village_repository.update_status(VillageStatus.IN_GAME)
        self.record_event(GameStartEvent(self.village))
        return self.village

    def reset(self):
        village = self.go_to_next_game()
        self.record_event(GameResetEvent(village))
        return village

    def end(self):
        winner = self.get_winner()
        self.record_event(GameEndEvent(self.village, winner))
        village = self.go_to_next_game()
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
        self.village = self.village_repository.increment_generation()
        return self.village

    def go_to_next_day(self):
        u""" 次の日に移る """
        if not self.in_game():
            raise GameException(u"ゲームは始まっていません")
        self.village = self.village_repository.increment_day()
        return self.village

    def get_residents(self, role=None):
        return self.village_repository.get_residents(role)

    def get_alive_residents(self, role=None):
        return self.village_repository.get_alive_residents(role)

    def get_resident(self, user):
        try:
            return self.village_repository.get_resident(user)
        except ResidentModel.DoesNotExist:
            raise GameException(u"%sさんは村に参加していません" % user.name)

    def join(self, user):
        if self.in_game():
            raise GameException(u"ゲームの開催中は参加できません")
        try:
            resident = ResidentModel.objects.get(
                village=self.village, user=user, generation=self.village.generation, role=None)
            raise GameException(u"%s さんは既に村に参加しています" % user.name)
        except ResidentModel.DoesNotExist as e:
            resident = ResidentModel.objects.create(
                village=self.village, user=user, generation=self.village.generation, role=None)
            self.record_event(JoinEvent(resident))
        return resident

    def leave(self, user):
        resident = self.get_resident(user)
        if self.in_game():
            raise GameException(u"ゲーム中は村から出られません。")
        resident.delete()
        self.record_event(LeaveEvent(resident))

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

    def set_execution_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を吊り対象にすることはできません")
        self.behavior_repository.create_or_update(
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
        self.behavior_repository.create_or_update(
            BehaviorType.ATTACK, resident, target_resident)

    def set_hunt_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role != Role.HUNTER:
            raise GameException(u"あなたは狩人ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を道連れにすることはできません")
        self.behavior_repository.create_or_update(
            BehaviorType.HUNT, resident, target_resident)

    def set_fortune_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role != Role.TELLER:
            raise GameException(u"あなたは占い師ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を占うことはできません")
        self.behavior_repository.create_or_update(
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
            resident = ResidentModel.objects.get(
                village=self.village, user=user, generation=self.village.generation)
        except ResidentModel.DoesNotExist:
            raise GameException(u"%s さんは村の住人ではありません" % user.name)
        if resident.status != ResidentStatus.ALIVE:
            raise GameException(u"%s さんは既に死んでいます" % user.name)
        return resident

    def execute_morning(self):
        village = self.go_to_next_day()
        self.record_event(MorningEvent(village))
        return village

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

        self.record_event(NightEvent(self.village, targets))

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
                behavior = self.behavior_repository.\
                           get_by_type_and_resident(behavior_type, r)
                voted.append(behavior.target_resident)
            except BehaviorModel.DoesNotExist:
                # ランダム選択. ここのロジックは Model に __eq__ が定義されてるからできる
                targets = [rr for rr in targets if rr != r]
                if targets:
                    voted.append(Util.shuffle(targets)[0])
        return Util.select_most_voted(voted)

    def store_message(self, user, message):
        u"""
        ゲーム開始状態でなければ誰でもメッセージを送れるが、
        ゲーム開始状態の場合は生きている参加者しかメッセージを送れない。
        """
        if self.in_game():
            self.ensure_alive_resident(user)
        event = MessageEvent(self.village, user, message)
        self.record_event(event)
        return event

    def record_event(self, event):
        event.to_model().save()
