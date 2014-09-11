# -*- coding: utf-8 -*-
import datetime
import uuid

from pyramid.renderers import JSON


def date_adapter(obj, request):
    return str(obj)


def datetime_adapter(obj, request):
    return obj.isoformat()


def uuid_adapter(obj, request):
    return obj.hex


json_renderer = JSON()
json_renderer.add_adapter(datetime.date, date_adapter)
json_renderer.add_adapter(datetime.datetime, datetime_adapter)
json_renderer.add_adapter(uuid.UUID, uuid_adapter)
