# -*- coding: utf-8 -*-
""" village """
# from django.db import models
# from django_extensions.db.models import TimeStampedModel
# from enumfields import EnumField, EnumIntegerField
from flywheel import Model, Field
from flywheel.fields.types import NUMBER, STRING

from werewolf.domain.base import EntityModel, ValueObject, register_enum_type


class ResidentStatus(ValueObject):
    """ Value Object """
    ALIVE = 1
    DEAD = 2

    class Labels:
        ALIVE = u'生存'
        DEAD = u'死亡'


class VillageStatus(ValueObject):
    u""" VO: 村の状態 """
    IN_GAME = 1
    OUT_GAME = 2

    class Labels:
        IN_GAME = u'進行中'
        OUT_GAME = u'募集中'


class Role(ValueObject):
    """ Value Object """

    WOLF = "wolf"
    VILLAGER = "villager"
    BERSERKER = "berserker"
    HUNTER = "hunter"
    TELLER = "teller"
    MEDIUM = "medium"

    class Labels:
        WOLF = u'人狼'
        VILLAGER = u'村人'
        BERSERKER = u'狂人'
        HUNTER = u'狩人'
        TELLER = u'占師'
        MEDIUM = u'霊媒師'

    def is_human(self):
        return self.value != self.WOLF


class BehaviorType(ValueObject):
    """ Value Object """

    EXECUTION = "execution"
    ATTACK = "attack"
    HUNT = "fortune"
    FORTUNE = "fortune"
    MEDIUM = "medium"

    class Labels:
        EXECUTION = u"投票"
        ATTACK = u"襲撃"
        FORTUNE = u"占い"
        HUNT = u"道連れ"
        MEDIUM = u"霊媒"


class Winner(ValueObject):
    WOLF = "wolf"
    HUMAN = "human"

    class Labels:
        WOLF = u"人狼"
        HUMAN = u"村人"


register_enum_type(ResidentStatus, NUMBER)
register_enum_type(VillageStatus, NUMBER)
register_enum_type(Role, STRING)
register_enum_type(BehaviorType, STRING)


class ResidentModel(EntityModel):
    u""" 村の住民 """

    village_id = Field(data_type='uuid', index='village-id-index')
    generation = Field(data_type=int)
    user_id = Field(data_type='uuid')
    status = Field(data_type='ResidentStatus')
    role = Field(data_type='Role')

    def update_status_(self, new_status):
        if self.status is not ResidentStatus.ALIVE:
            raise AttributeError
        self.status = new_status

    def to_dict(self):
        return dict(
            identity=self.identity,
            village_id=self.village_id,
            user_id=self.user_id,
            status=self.status.name,
            role=self.role,
        )

class GameModel(EntityModel):
    u""" 村で開催されるゲームのモデル """
    village_id = Field(data_type='uuid', index='village-id-index')
    generation = Field(data_type=int)  # 第X回として参照されるだけ
    day = Field(data_type=int)


class VillageModel(EntityModel):
    u""" 村のモデル

    Repository から永続データを取得すると、そこに紐付いている
    住人が自動的に _residents に付与される。
    """
    DAYTIME_LENGTH = 10  # 10 sec

    name = Field(data_type=unicode)
    status = Field(data_type='VillageStatus')
    generation = Field(data_type=int)
    day = Field(data_type=int)

    def __init__(self, *args, **kwargs):
        _kwargs = dict(
            status=VillageStatus.OUT_GAME,
            generation=1,
            day=1,
        )
        _kwargs.update(kwargs)
        super(VillageModel, self).__init__(*args, **_kwargs)

    def to_dict(self):
        return dict(
            identity=self.identity.hex,
            name=self.name,
            status=self.status.name,
            day=self.day,
            # start_at=self.start_at,
            # end_at=self.end_at,
            created=self.created,
            modified=self.modified)


class BehaviorModel(EntityModel):
    u""" 特定の回の村の、特定の日の、住人の行動を記録 """

    behavior_type = Field(data_type='BehaviorType')
    village_id = Field(data_type='uuid')
    generation = Field(data_type=int)
    day = Field(data_type=int)
    resident_id = Field(data_type='uuid')
    target_resident_id = Field(data_type='uuid')


# class ResidentModel(EntityModel):
#     u""" 村の住民 """

#     village = models.ForeignKey('VillageModel')
#     generation = models.IntegerField()
#     user = models.ForeignKey('User')
#     status = EnumIntegerField(ResidentStatus, default=ResidentStatus.ALIVE)
#     role = EnumField(Role, max_length=20, null=True)

#     def update_status(self, new_status):
#         if self.status is not ResidentStatus.ALIVE:
#             raise AttributeError
#         self.status = new_status

#     def to_dict(self):
#         return dict(
#             identity=self.identity,
#             village_id=self.village_id,
#             user_id=self.user_id,
#             status=self.status.name,
#             role=self.role,
#         )

#     def __unicode__(self):
#         return u"{} ({})".format(self.user.name, self.village.name)

#     class Meta:
#         app_label = 'werewolf'
#         db_table = 'werewolf_resident'


# class VillageModel(EntityModel):
#     """ village, which is a unit of games """
#     DAYTIME_LENGTH = 10  # 10 sec

#     name = models.CharField(max_length=100)
#     status = EnumIntegerField(VillageStatus, default=VillageStatus.OUT_GAME)
#     generation = models.IntegerField(default=1)
#     day = models.IntegerField(default=1)

#     def to_dict(self):
#         return dict(
#             identity=self.identity,
#             name=self.name,
#             status=self.status.name,
#             day=self.day,
#             # start_at=self.start_at,
#             # end_at=self.end_at,
#             created=self.created,
#             modified=self.modified)

#     def increment_day(self):
#         if self.status != VillageStatus.IN_GAME:
#             raise RuntimeError
#         self.day = self.day + 1

#     def __unicode__(self):
#         return self.name

#     class Meta:
#         app_label = 'werewolf'
#         db_table = 'werewolf_village'


# class BehaviorModel(EntityModel):
#     u""" 特定の回の村の、特定の日の、住人の行動を記録 """

#     behavior_type = EnumField(BehaviorType, max_length=20)
#     village = models.ForeignKey('VillageModel')
#     generation = models.IntegerField()
#     day = models.IntegerField()
#     resident = models.ForeignKey('ResidentModel', related_name='behavior_set')
#     target_resident = models.ForeignKey('ResidentModel', related_name='targeted_behavior_set')

#     class Meta:
#         app_label = 'werewolf'
#         db_table = 'werewolf_behavior'
