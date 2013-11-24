# -*- encoding: utf-8 -*-
""" village """
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .base import EntityModel


class Resident(EntityModel):
    u""" 村の住民 """
    ROLE_WOLF = "wolf"
    ROLE_VILLAGER = "villager"
    ROLE_BERSERKER = "berserker"
    ROLE_FORTUNE_TELLER = "fortune_teller"
    ROLE_PHANTOM_THIEF = "phantom_thief"

    ROLE_CHOICES = (
        (ROLE_WOLF, u'人狼'),
        (ROLE_VILLAGER, u'村人'),
        (ROLE_BERSERKER, u'狂人'),
        (ROLE_FORTUNE_TELLER, u'占い師'),
        (ROLE_PHANTOM_THIEF, u'怪盗'),
    )

    STATUS_ALIVE = 1
    STATUS_EXECUTED = 2
    STATUS_ATTACKED = 3

    STATUS_CHOICES = (
        (STATUS_ALIVE, 'alive'),
        (STATUS_EXECUTED, 'executed'),
        (STATUS_ATTACKED, 'attacked'),
    )

    village = models.ForeignKey('Village')
    user = models.ForeignKey('User')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ALIVE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True)
    # is_winner = models.NullBooleanField(null=True)
    # execution_target = models.ForeignKey('Resident', null=True)
    # hunt_target = models.ForeignKey('Resident', null=True)

    def update_status(self, new_status):
        if self.status != self.STATUS_ALIVE:
            raise AttributeError
        self.status = new_status

    class Meta:
        app_label = 'werewolf'


class Village(EntityModel):
    """ village, which is a unit of games """
    DAYTIME_LENGTH = 10  # 10 sec

    STATUS_PREPARING = 1
    STATUS_PROLOGUE = 2
    STATUS_IN_GAME = 3
    STATUS_EPILOGUE = 4
    STATUS_CLOSED = 5

    STATUS_CHOICES = (
        (STATUS_PREPARING, 'preparing'),
        (STATUS_PROLOGUE, 'prologue'),
        (STATUS_IN_GAME, 'in_game'),
        (STATUS_EPILOGUE, 'epilogue'),
        (STATUS_CLOSED, 'closed'),
    )

    allowed_transitions = {
        STATUS_PREPARING: [STATUS_PROLOGUE],
        STATUS_PROLOGUE: [STATUS_IN_GAME],
        STATUS_IN_GAME: [STATUS_EPILOGUE],
        STATUS_EPILOGUE: [STATUS_CLOSED]}

    WINNER_VILLAGER = 1
    WINNER_WOLF = 2

    WINNER_CHOICES = (
        (WINNER_VILLAGER, u'村人の勝利'),
        (WINNER_WOLF, u'人狼の勝利'),
    )

    ROLES = [
        Resident.ROLE_WOLF,
        Resident.ROLE_VILLAGER,
        Resident.ROLE_VILLAGER,
        Resident.ROLE_VILLAGER,
        Resident.ROLE_VILLAGER,
        ]

    name = models.CharField(max_length=100)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PREPARING)
    day = models.IntegerField(default=0)

    # start_at = models.DateTimeField(null=True)
    # end_at = models.DateTimeField(null=True)
    # winner = models.CharField(max_length=20, choices=WINNER_CHOICES)

    def to_dict(self):
        return dict(
            identity=self.identity,
            name=self.name,
            status=self.get_status_display(),
            start_at=self.start_at,
            end_at=self.end_at,
            created=self.created,
            modified=self.modified)

    def update_status(self, new_status):
        allowed_status = self.allowed_transitions.get(self.status, [])
        if new_status not in allowed_status:
            raise AttributeError
        self.status = new_status

    def increment_day(self):
        if self.status != self.STATUS_IN_GAME:
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
