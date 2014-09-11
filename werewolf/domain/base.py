# -*- coding: utf-8 -*-
""" base entity model """
import datetime
import inspect
import json
import uuid

from enum import Enum, EnumMeta
from flywheel import Model, Field
from flywheel.fields.types import TypeDefinition, NUMBER, STRING, register_type

__all__ = ["Identity", "EntityModel", "ValueObject"]


class Identity(object):
    u""" 識別子を表す Value Object

    - Entity の識別子として利用
    - None を保持できる
    - value 属性で UUID にアクセスできる
    """

    def __init__(self, value):
        if isinstance(value, Identity):
            self._value = value.value
        elif value in (None, ""):
            self._value = None
        elif isinstance(value, uuid.UUID):
            self._value = value
        elif isinstance(value, basestring):
            self._value = uuid.UUID(value)
        elif isinstance(value, int):
            self._value = uuid.UUID(int=value)
        else:
            raise ValueError()

    @classmethod
    def create(cls):
        return cls(uuid.uuid4())

    @property
    def value(self):
        u""" UUID または None """
        return self._value

    @property
    def hex(self):
        return self._value.hex if self._value else ""

    def is_empty(self):
        return self._value is None

    def __nonzero__(self):
        return not self.is_empty()

    def __eq__(self, other):
        return self._value == other.value

    def __ne__(self, other):
        return self._value != other.value

    def __str__(self):
        return str(self._value) if self._value else ""

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return "<Identity '{}'>".format(str(self))

    def __json__(self, request):
        return self.hex


class IdentityType(TypeDefinition):
    u""" Identity Type """

    data_type = Identity
    aliases = ['identity']
    ddb_data_type = STRING

    def ddb_dump(self, value):
        u""" DynamoDB へ書き出す際の変換 """
        return value.hex

    def ddb_load(self, value):
        u""" DynamoDB から読み込む際の変換 """
        return Identity(value)

register_type(IdentityType)


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


class EntityModel(Model):
    u""" Entity Model """

    identity = Field(data_type='identity', hash_key=True)
    created = Field(data_type=datetime.datetime, range_key=True)
    modified = Field(data_type=datetime.datetime)

    def __init__(self, *args, **kwargs):
        _kwargs = dict(
            identity=Identity.create(),
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

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self._value_ >= other._value_
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self._value_ > other._value_
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self._value_ <= other._value_
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self._value_ < other._value_
        return NotImplemented
