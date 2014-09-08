# -*- coding: utf-8 -*-
""" base entity model """
import datetime
import inspect
import json
import uuid

from enum import Enum, EnumMeta
from flywheel import Model, Field
from flywheel.fields.types import TypeDefinition, NUMBER, STRING, register_type

# from django.db import models
# from django_extensions.db.models import TimeStampedModel
# from django_extensions.db.fields import UUIDField

__all__ = ["EntityModel", "ValueObject"]


# class EntityModel(TimeStampedModel):
#     identity = UUIDField(version=1, auto=True, primary_key=True)

#     def __eq__(self, other):
#         return self.identity == other.identity

#     def __ne__(self, other):
#         return self.identity != other.identity

#     class Meta:
#         abstract = True

def register_enum_type(type_class, _ddb_data_type):
    u""" Enum 型の data_type を登録する """

    class EnumType(TypeDefinition):
        u""" Enum Type for {} """.format(type_class.__name__)
        data_type = type_class
        aliases = [type_class.__name__]
        ddb_data_type = _ddb_data_type

        def ddb_dump(self, value):
            u""" DynamoDB へ書き出す際の変換 """
            return value.value

        def ddb_load(self, value):
            u""" DynamoDB から読み込む際の変換 """
            return type_class(value)

    register_type(EnumType)


class UUIDType(TypeDefinition):
    u""" UUID Type """

    data_type = uuid.UUID
    aliases = ['uuid']
    ddb_data_type = STRING

    def ddb_dump(self, value):
        u""" DynamoDB へ書き出す際の変換 """
        return value.hex

    def ddb_load(self, value):
        u""" DynamoDB から読み込む際の変換 """
        return uuid.UUID(hex=value)

register_type(UUIDType)


class EntityModel(Model):
    u""" Entity Model """

    identity = Field(data_type='uuid', hash_key=True)
    created = Field(data_type=datetime.datetime, range_key=True)
    modified = Field(data_type=datetime.datetime)

    def __init__(self, *args, **kwargs):
        _kwargs = dict(
            identity=uuid.uuid4(),
            created=datetime.datetime.utcnow(),
            modified=datetime.datetime.utcnow(),
        )
        _kwargs.update(kwargs)
        super(EntityModel, self).__init__(*args, **_kwargs)

    __metadata__ = {
        '_abstract': True,
    }


class LabeledEnumMeta(EnumMeta):
    def __new__(cls, name, bases, attrs):
        Labels = attrs.get('Labels')

        if Labels is not None and inspect.isclass(Labels):
            del attrs['Labels']

        obj = EnumMeta.__new__(cls, name, bases, attrs)
        for m in obj:
            try:
                m.label = getattr(Labels, m.name)
            except AttributeError:
                m.label = m.name.replace('_', ' ').title()

        return obj


class LabeledEnum(Enum):
    """ Enum which can also define labels. ported from django_enumfields """
    __metaclass__ = LabeledEnumMeta

    @classmethod
    def choices(cls):
        return tuple((m.value, m.label) for m in cls)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.label


class ValueObject(LabeledEnum):
    """ Base class for Value Object """
    pass
