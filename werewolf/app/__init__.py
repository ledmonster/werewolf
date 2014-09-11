# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()


import datetime
import os

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from werewolf.app.authn import OAuth2AuthenticationPolicy


def add_static_view(config, dir_name, view_root=None, cache_max_age=3600):
    config.add_static_view(
        dir_name,
        os.path.join('static', view_root if view_root is not None else dir_name),
        cache_max_age=cache_max_age,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """

    authn_policy = OAuth2AuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory='werewolf.app.resource.RootResource',
        default_permission='authenticated'
    )
    config.include('pyramid_jinja2')
    config.add_renderer(".html", "pyramid_jinja2.renderer_factory")
    config.add_renderer('json', "werewolf.app.renderer.json_renderer")

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    add_static_view(config, 'bower_components')
    add_static_view(config, 'css')
    add_static_view(config, 'scripts')
    add_static_view(config, 'static', '')

    config.add_route('layout', '/')

    config.add_route('api_user', '/api/v1/user')
    config.add_route('api_user_nickname_update', '/api/v1/user/nickname/update')
    config.add_route('api_auth_token', '/api/v1/auth/token')

    config.add_route('api_village_list', '/api/v1/village/list')
    config.add_route('api_village_detail', '/api/v1/village/{identity}')
    config.add_route('api_village_join', '/api/v1/village/join')

    config.add_route('socketio', '/socket.io/*remaining')

    config.scan()
    return config.make_wsgi_app()
