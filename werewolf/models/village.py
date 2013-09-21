# -*- encoding: utf-8 -*-
""" village """
import uuid

from django.db import models
from uuidfield import UUIDField


class Village(models.Model):
    """ village """
    STATUS_OPEN = 1
    STATUS_IN_PROGRESS = 2
    STATUS_CLOSED = 3

    STATUS_CHOICES = (
        (STATUS_OPEN, 'open'),
        (STATUS_IN_PROGRESS, 'in progress'),
        (STATUS_CLOSED, 'closed'),
    )

    identity = UUIDField(version=1, auto=True, primary_key=True)
    name = models.CharField(max_length=100)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_OPEN)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'


class Player(models.Model):
    """ player """

    identity = UUIDField(version=1, auto=True, primary_key=True)
    user = models.ForeignKey('User')
    character = models.ForeignKey('Character')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'


class Character(models.Model):
    """ character """
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    STATUS_CHOICES = (
        (STATUS_ENABLED, 'enabled'),
        (STATUS_DISABLED, 'disabled'),
    )

    identity = UUIDField(version=1, auto=True, primary_key=True)
    name = models.CharField(max_length=100)
    job = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to="charactor/")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ENABLED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'


class PlayerRole(models.Model):
    u""" 村での Player の役職 """
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

    identity = UUIDField(version=1, auto=True, primary_key=True)
    village = models.ForeignKey('Village')
    player = models.ForeignKey('Player')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ALIVE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'


class GameResult(models.Model):
    """ play result """

    WINNER_VILLAGER = 1
    WINNER_WOLF = 2

    WINNER_CHOICES = (
        (WINNER_VILLAGER, u'村人の勝利'),
        (WINNER_WOLF, u'人狼の勝利'),
    )

    village = models.OneToOneField('Village', primary_key=True)
    winner = models.CharField(max_length=20, choices=WINNER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'werewolf'
