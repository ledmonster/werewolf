# -*- encoding: utf-8 -*-
""" village """
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .base import EntityModel


class ResidentStatus(object):
    """ Value Object """
    ALIVE = 1
    DEAD = 2

    LABELS = (
        (ALIVE, 'alive'),
        (DEAD, 'dead'),
    )

    def __init__(self, value):
        self.value = value


class VillageStatus(object):
    u""" VO: 村の状態 """
    IN_GAME = 1
    OUT_GAME = 2

    LABELS = (
        (IN_GAME, u'進行中'),
        (OUT_GAME, u'募集中'),
    )

    def __init__(self, value):
        self.value = value


class Role(object):
    """ Value Object """

    WOLF = "wolf"
    VILLAGER = "villager"
    BERSERKER = "berserker"
    HUNTER = "hunter"

    LABELS = (
        (WOLF, u'人狼'),
        (VILLAGER, u'村人'),
        (BERSERKER, u'狂人'),
        (HUNTER, u'狩人'),
    )

    def __init__(self, value):
        self.value = value

    def is_human(self):
        return self.value != self.WOLF

class Resident(EntityModel):
    u""" 村の住民 """

    village = models.ForeignKey('Village')
    user = models.ForeignKey('User')
    status = models.SmallIntegerField(
        choices=ResidentStatus.LABELS,
        default=ResidentStatus.ALIVE)
    role = models.CharField(
        max_length=20,
        choices=Role.LABELS,
        null=True)
    # is_winner = models.NullBooleanField(null=True)
    # execution_target = models.ForeignKey('Resident', null=True)
    # hunt_target = models.ForeignKey('Resident', null=True)

    def update_status(self, new_status):
        if self.status != ResidentStatus.ALIVE:
            raise AttributeError
        self.status = new_status

    class Meta:
        app_label = 'werewolf'


class Village(EntityModel):
    """ village, which is a unit of games """
    DAYTIME_LENGTH = 10  # 10 sec

    WINNER_VILLAGER = 1
    WINNER_WOLF = 2

    WINNER_CHOICES = (
        (WINNER_VILLAGER, u'村人の勝利'),
        (WINNER_WOLF, u'人狼の勝利'),
    )

    name = models.CharField(max_length=100)
    status = models.SmallIntegerField(
        choices=VillageStatus.LABELS,
        default=VillageStatus.OUT_GAME)
    day = models.IntegerField(default=0)

    # start_at = models.DateTimeField(null=True)
    # end_at = models.DateTimeField(null=True)
    # winner = models.CharField(max_length=20, choices=WINNER_CHOICES)

    def to_dict(self):
        return dict(
            identity=self.identity,
            name=self.name,
            status=self.get_status_display(),
            day=self.day,
            # start_at=self.start_at,
            # end_at=self.end_at,
            created=self.created,
            modified=self.modified)

    def update_status(self, new_status):
        self.status = new_status

    def increment_day(self):
        if self.status != VillageStatus.IN_GAME:
            raise RuntimeError
        self.day = self.day + 1

    class Meta:
        app_label = 'werewolf'


class Behavior(EntityModel):

    TYPE_EXECUTION = "execution"
    TYPE_ATTACK = "attack"
    TYPE_FORTUNE_TELLING = "fortune_telling"

    TYPE_CHOICES = (
        (TYPE_EXECUTION, TYPE_EXECUTION),
        (TYPE_ATTACK, TYPE_ATTACK),
        (TYPE_FORTUNE_TELLING, TYPE_FORTUNE_TELLING),
        )

    behavior_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    village = models.ForeignKey('Village')
    day = models.IntegerField()
    resident = models.ForeignKey('Resident', related_name='behavior_set')
    target_resident = models.ForeignKey('Resident', related_name='targeted_behavior_set')

    class Meta:
        app_label = 'werewolf'
