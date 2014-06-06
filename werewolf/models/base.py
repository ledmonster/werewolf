# -*- encoding: utf-8 -*-
""" base entity model """
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField


class EntityModel(TimeStampedModel):
    identity = UUIDField(version=1, auto=True, primary_key=True)

    def __eq__(self, other):
        return self.identity == other.identity

    def __ne__(self, other):
        return self.identity != other.identity

    class Meta:
        abstract = True


class ValueObject(object):
    """ Base class for Value Object """
    def __init__(self, value):
        if value not in dict(self.LABELS):
            raise ValueError("invalid value: %s" % value)
        self.value = value

    def __str__(self, other):
        return self.value

    def __unicode__(self, other):
        return self.value

    @property
    def label(self):
        return dict(self.LABELS)[self.value]
