# -*- coding: utf-8 -*-
import datetime
import os

from pyramid.config import Configurator
from pyramid.renderers import JSON

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"



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

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('village_list', '/village/list')
    config.add_route('village_detail', '/village/{identity}')

    config.add_route('api_village_list', '/api/v1/village/list')
    config.add_route('api_village_join', '/api/v1/village/join')
    config.add_route('api_auth_token', '/api/v1/auth/token')

    config.scan()
    return config.make_wsgi_app()
