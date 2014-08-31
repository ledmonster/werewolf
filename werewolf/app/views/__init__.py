# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.view import notfound_view_config


@notfound_view_config(renderer='layout.html', xhr=False)
@view_config(route_name='layout', renderer='layout.html')
def index(request):
    return {}
