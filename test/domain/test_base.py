# -*- coding: utf-8 -*-
from enum import Enum
from flywheel.fields.types import NUMBER, register_type, ALL_TYPES

from werewolf.domain.base import register_enum_type


def test_register_enum_type():
    class Status(Enum):
        ENABLED = 1
        DISABLED = 2

    register_enum_type(Status, NUMBER)
    assert "Status" in ALL_TYPES
