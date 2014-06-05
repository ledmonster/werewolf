# -*- encoding: utf-8 -*-
""" village """
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .base import EntityModel


class ValueObject(object):
    """ Base class for Value Object """
    def __init__(self, value):
        if value not in dict(self.LABELS):
            raise ValueError("invalid value: %s" % value)
        self.value = value

    @property
    def label(self):
        return dict(self.LABELS)[self.value]


class ResidentStatus(ValueObject):
    """ Value Object """
    ALIVE = 1
    DEAD = 2

    LABELS = (
        (ALIVE, u'生存'),
        (DEAD, u'死亡'),
    )


class VillageStatus(ValueObject):
    u""" VO: 村の状態 """
    IN_GAME = 1
    OUT_GAME = 2

    LABELS = (
        (IN_GAME, u'進行中'),
        (OUT_GAME, u'募集中'),
    )


class Role(ValueObject):
    """ Value Object """

    WOLF = "wolf"
    VILLAGER = "villager"
    BERSERKER = "berserker"
    HUNTER = "hunter"
    TELLER = "teller"
    MEDIUM = "medium"

    LABELS = (
        (WOLF, u'人狼'),
        (VILLAGER, u'村人'),
        (BERSERKER, u'狂人'),
        (HUNTER, u'狩人'),
        (TELLER, u'占師'),
        (MEDIUM, u'霊媒師'),
    )

    def is_human(self):
        return self.value != self.WOLF


class BehaviorType(ValueObject):
    """ Value Object """

    EXECUTION = "execution"
    ATTACK = "attack"
    HUNT = "fortune"
    FORTUNE = "fortune"
    MEDIUM = "medium"

    LABELS = (
        (EXECUTION, u"投票"),
        (ATTACK, u"襲撃"),
        (FORTUNE, u"占い"),
        (HUNT, u"道連れ"),
        (MEDIUM, u"霊媒"),
    )


class Winner(ValueObject):
    WOLF = "wolf"
    HUMAN = "human"

    LABELS = (
        (WOLF, u"狼"),
        (HUMAN, u"人間"),
    )


class Resident(EntityModel):
    u""" 村の住民 """

    village = models.ForeignKey('Village')
    generation = models.IntegerField()
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

    def to_dict(self):
        return dict(
            identity=self.identity,
            village_id=self.village_id,
            user_id=self.user_id,
            status=self.get_status_display(),
            role=self.role,
        )

    def __unicode__(self):
        return u"%s (%s)" % (self.user.name, self.village.name)

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
    generation = models.IntegerField(default=1)
    day = models.IntegerField(default=1)

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

    def increment_day(self):
        if self.status != VillageStatus.IN_GAME:
            raise RuntimeError
        self.day = self.day + 1

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'werewolf'


class Behavior(EntityModel):
    u""" 特定の回の村の、特定の日の、住人の行動を記録 """

    behavior_type = models.CharField(max_length=20, choices=BehaviorType.LABELS)
    village = models.ForeignKey('Village')
    generation = models.IntegerField()
    day = models.IntegerField()
    resident = models.ForeignKey('Resident', related_name='behavior_set')
    target_resident = models.ForeignKey('Resident', related_name='targeted_behavior_set')

    class Meta:
        app_label = 'werewolf'
