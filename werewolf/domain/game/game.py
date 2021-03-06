# -*- coding: utf-8 -*-
""" Kind of domain layer in this application.
Game class aggregates objects behind this game. """

import random

from werewolf.domain.user import *
from werewolf.domain.game import *
from werewolf.domain.game.exception import GameException, GameNotFinished
import werewolf.infra.util as util


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


class GameService(object):
    u""" 村のゲーム運営を行うサービス """

    def __init__(self, context, village_id):
        self.repo_user = context.repos['user']
        self.repo_village = context.repos['village']
        self.repo_resident = context.repos['resident']
        self.repo_event = context.repos['event']
        self.repo_behavior = context.repos['behavior']
        self.village = self.repo_village.get_entity(village_id)

    def start(self):
        if self.village.in_game():
            raise GameException(u"既にゲームは始まっています")

        # temporary logic for demo
        com1 = self.repo_user.get('d4d8722d-3c15-4eee-9a76-dcc30bcd272f');
        com2 = self.repo_user.get('c7a7f5fa-8113-40b1-9fd7-a4e07ceb89f2');
        com3 = self.repo_user.get('be5ff2bf-f72f-44ee-a792-15e6f24ebf11');

        self.join(com1)
        self.join(com2)
        self.join(com3)

        residents = self.assign_roles(self.village.get_residents())
        self.village = self.repo_village.update_status(
            self.village.identity, VillageStatus.IN_GAME)
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
        residents = self.village.get_alive_residents()
        wolves = [r for r in residents if r.role is Role.WOLF]
        humans = [r for r in residents if r.role is not Role.WOLF]
        if len(wolves) == 0:
            return Winner.HUMAN
        elif len(wolves) >= len(humans):
            return Winner.WOLF
        raise GameNotFinished(u"まだゲームは終わっていません")

    def go_to_next_game(self):
        u""" generation を increment して次のゲームを始める """
        if not self.village.in_game():
            raise GameException(u"ゲームは始まっていません")
        self.village = self.repo_village.increment_generation(
            self.village.identity)

        return self.village

    def go_to_next_day(self):
        u""" 次の日に移る """
        if not self.village.in_game():
            raise GameException(u"ゲームは始まっていません")
        self.village = self.repo_village.increment_day(
            self.village.identity)
        return self.village

    def join(self, user):
        if self.village.in_game():
            raise GameException(u"ゲームの開催中は参加できません")
        if self.village.is_resident(user):
            raise GameException(u"{} さんは既に村に参加しています".format(user.name))
        resident = self.repo_resident.add_by_village_and_user(
            self.village, user)
        self.record_event(JoinEvent(resident))
        return resident

    def leave(self, user):
        resident = self.village.get_resident(user)
        if resident is None:
            raise GameException(u"{}さんは村に参加していません".format(user.name))
        if self.village.in_game():
            raise GameException(u"ゲーム中は村から出られません。")
        self.repo_resident.delete(resident)
        self.record_event(LeaveEvent(resident))

    def get_role_constitution(self):
        if not self.village.in_game():
            raise GameException(u"まだゲームは始まっていません")
        residents = self.village.get_residents()
        roles = [r.role for r in residents]
        return sorted(roles)

    def assign_roles(self, residents):
        num_residents = len(residents)
        if num_residents < 1:
            raise GameException(u"住人が少なすぎます")
        elif num_residents > 6:
            raise GameException(u"住人が多すぎます")
        roles = util.shuffle(random.choice(MEMBER_TYPES[num_residents]))
        for i, resident in enumerate(residents):
            residents[i] = self.repo_resident.assign_role(resident, roles[i])
        return residents

    def set_execution_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を吊り対象にすることはできません")
        self.repo_behavior.create_or_update(
            self.village,
            BehaviorType.EXECUTION,
            resident.identity,
            target_resident.identity
        )

    def set_attack_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role is not Role.WOLF:
            raise GameException(u"あなたは狼ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を襲撃することはできません")
        if target_resident.role is Role.WOLF:
            raise GameException(u"仲間を襲撃することはできません")
        self.repo_behavior.create_or_update(
            self.village,
            BehaviorType.ATTACK,
            resident.identity,
            target_resident.identity
        )

    def set_hunt_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role is not Role.HUNTER:
            raise GameException(u"あなたは狩人ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を道連れにすることはできません")
        self.repo_behavior.create_or_update(
            self.village,
            BehaviorType.HUNT,
            resident.identity,
            target_resident.identity
        )

    def set_fortune_target(self, user, target_name):
        resident = self.ensure_alive_resident(user)
        if resident.role is not Role.TELLER:
            raise GameException(u"あなたは占い師ではありません")
        target_user = self.get_user_by_name(target_name)
        target_resident = self.ensure_alive_resident(target_user)
        if resident.user.identity == target_resident.user.identity:
            raise GameException(u"自分自身を占うことはできません")
        self.repo_behavior.create_or_update(
            self.village,
            BehaviorType.FORTUNE,
            resident.identity,
            target_resident.identity
        )

    def get_user_by_name(self, name):
        u""" 名前をもとにユーザを取得(TODO: 同じ名前の人対応) """
        try:
            return self.repo_user.get_by_name(name)
        except ValueError:
            raise GameException(u"{} という名前の人はいません".format(name))

    def ensure_alive_resident(self, user):
        u""" user がゲーム中の村の生きた住人であることを保障 """
        if not self.village.in_game():
            raise GameException(u"まだゲームは始まってません")
        resident = self.village.get_resident(user)
        if resident is None:
            raise GameException(u"{}さんは村に参加していません".format(user.name))
        if resident.status is not ResidentStatus.ALIVE:
            raise GameException(u"{} さんは既に死んでいます".format(user.name))
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

        if not self.village.in_game():
            raise GameException(u"ゲームは開始されていません")

        targets = {}

        # 占い
        residents = self.village.get_alive_residents()
        targets['fortune'] = self.select_fortune_target(residents)

        # 吊り
        targets['execution'] = self.select_execution_target(residents)
        if targets['execution']:
            residents = self.kill_resident(targets['execution'])
            if targets['execution'].role is Role.HUNTER:
                targets['hunt'] = self.select_hunt_target(residents)
                residents = self.kill_resident(targets['hunt'])

        # 襲撃
        targets['attack'] = self.select_attack_target(residents)
        if targets['attack']:
            residents = self.kill_resident(targets['attack'])
            if targets['execution'].role is Role.HUNTER:
                targets['hunt'] = self.select_hunt_target(residents)
                residents = self.kill_resident(targets['hunt'])

        self.record_event(NightEvent(self.village, targets))

        return targets

    def kill_resident(self, resident):
        u""" 住民が死ぬ """
        if resident:
            self.repo_resident.update_status(resident, ResidentStatus.DEAD)
        return self.village.get_alive_residents()

    def select_execution_target(self, residents):
        u""" 吊り対象を選ぶ """
        return self.select_action_target(BehaviorType.EXECUTION, residents, residents)

    def select_attack_target(self, residents):
        humans = [r for r in residents if r.role is not Role.WOLF]
        wolves = [r for r in residents if r.role is Role.WOLF]
        return self.select_action_target(BehaviorType.ATTACK, wolves, humans)

    def select_hunt_target(self, residents):
        hunters = [r for r in residents if r.role is Role.HUNTER]
        return self.select_action_target(BehaviorType.HUNT, hunters, residents)

    def select_fortune_target(self, residents):
        tellers = [r for r in residents if r.role is Role.TELLER]
        return self.select_action_target(BehaviorType.FORTUNE, tellers, residents)

    def select_action_target(self, behavior_type, executors, targets):
        voted = []
        for r in executors:
            try:
                behavior = self.repo_behavior.\
                           get_by_type_and_resident(self.village, behavior_type, r.identity)
                voted.append(behavior.target_resident_id)
            except ValueError:
                my_targets = [rr.identity for rr in targets if rr.identity != r.identity]
                if my_targets:
                    voted.append(util.shuffle(my_targets)[0])

        most_voted_id = util.select_most_voted(voted)
        if most_voted_id:
            return self.repo_resident.get(most_voted_id)
        return None

    def store_message(self, user, message):
        u"""
        ゲーム開始状態でなければ誰でもメッセージを送れるが、
        ゲーム開始状態の場合は生きている参加者しかメッセージを送れない。
        """
        if self.village.in_game():
            self.ensure_alive_resident(user)
        event = MessageEvent(self.village, user, message)
        self.record_event(event)
        return event

    def record_event(self, event):
        return self.repo_event.add(event)

    def get_current_events(self):
        return self.repo_event.get_current_events(self.village)
