# -*- encoding: utf-8 -*-
""" village """
from django.db import models
from django_extensions.db.models import TimeStampedModel

from .base import EntityModel


class Village(EntityModel):
    """ village """
    STATUS_OPEN = 1
    STATUS_IN_PROGRESS = 2
    STATUS_CLOSED = 3

    STATUS_CHOICES = (
        (STATUS_OPEN, 'open'),
        (STATUS_IN_PROGRESS, 'in progress'),
        (STATUS_CLOSED, 'closed'),
    )

    WINNER_VILLAGER = 1
    WINNER_WOLF = 2

    WINNER_CHOICES = (
        (WINNER_VILLAGER, u'村人の勝利'),
        (WINNER_WOLF, u'人狼の勝利'),
    )

    name = models.CharField(max_length=100)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_OPEN)
    start_at = models.DateTimeField(null=True)
    end_at = models.DateTimeField(null=True)
    winner = models.CharField(max_length=20, choices=WINNER_CHOICES)

    def to_dict(self):
        return dict(
            identity=self.identity,
            name=self.name,
            status=self.get_status_display(),
            start_at=self.start_at,
            end_at=self.end_at,
            created=self.created,
            modified=self.modified)

    class Meta:
        app_label = 'werewolf'


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

    STATUS_CHOICES = (
        (STATUS_ALIVE, 'alive'),
        (STATUS_EXECUTED, 'executed'),
    )

    village = models.ForeignKey('Village')
    user = models.ForeignKey('User')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ALIVE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_winner = models.BooleanField(null=True)
    execution_target = models.ForeignKey('Resident', null=True)
    hunt_target = models.ForeignKey('Resident', null=True)

    class Meta:
        app_label = 'werewolf'
