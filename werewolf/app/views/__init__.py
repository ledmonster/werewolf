# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.view import notfound_view_config


@notfound_view_config(renderer='layout.html', xhr=False)
@view_config(route_name='layout', renderer='layout.html')
def index(request):
    return {}


@view_config(route_name='village_detail', renderer='village/detail.html')
def village_detail(request):
    identity = request.matchdict.get('identity')
    try:
        village = VillageModel.objects.get(identity=identity)
    except VillageModel.DoesNotExist:
        raise NotFound('page not found')

    return dict(village=village)
