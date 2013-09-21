""" base entity model """
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField


class EntityModel(TimeStampedModel):
    identity = UUIDField(version=1, auto=True, primary_key=True)

    class Meta:
        abstract = True
