# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()


import datetime
import os

from pyramid.config import Configurator
from pyramid.renderers import JSON

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"


def add_static_view(config, dir_name, view_root=None, cache_max_age=3600):
    config.add_static_view(
        dir_name,
        os.path.join('static', view_root if view_root is not None else dir_name),
        cache_max_age=cache_max_age,
    )


def datetime_adapter(obj, request):
        return obj.isoformat()


json_renderer = JSON()
json_renderer.add_adapter(datetime.datetime, datetime_adapter)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_renderer(".html", "pyramid_jinja2.renderer_factory")
    config.add_renderer('json', json_renderer)

    add_static_view(config, 'bower_components')
    add_static_view(config, 'css')
    add_static_view(config, 'js')
    add_static_view(config, 'scripts')
    add_static_view(config, 'static', '')

    config.add_route('layout', '/')
    config.add_route('village_list', '/village/list')
    config.add_route('village_detail', '/village/{identity}')

    config.add_route('api_village_list', '/api/v1/village/list')
    config.add_route('api_village_join', '/api/v1/village/join')
    config.add_route('api_auth_token', '/api/v1/auth/token')

    config.add_route('socketio', '/socket.io/*remaining')

    config.scan()
    return config.make_wsgi_app()
