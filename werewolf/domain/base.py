# -*- coding: utf-8 -*-
""" base entity model """
import inspect

from enum import Enum, EnumMeta
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField

__all__ = ["EntityModel", "ValueObject"]


class EntityModel(TimeStampedModel):
    identity = UUIDField(version=1, auto=True, primary_key=True)

    def __eq__(self, other):
        return self.identity == other.identity

    def __ne__(self, other):
        return self.identity != other.identity

    class Meta:
        abstract = True


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
