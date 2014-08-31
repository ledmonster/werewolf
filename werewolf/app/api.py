# -*- coding: utf-8 -*-
""" api server """
import datetime

from pyramid.view import view_config
import pyramid.httpexceptions as exc

from werewolf.domain.game.models import *
from werewolf.domain.user.models import *
from werewolf.domain.user.exception import *


@view_config(route_name='home', renderer='index.html')
def index(request):
    return {}


@view_config(route_name='village_list', renderer='village/list.html')
def village_list(request):
    return {}


@view_config(route_name='village_detail', renderer='village/detail.html')
def village_detail(request):
    identity = request.matchdict.get('identity')
    try:
        village = VillageModel.objects.get(identity=identity)
    except VillageModel.DoesNotExist:
        raise NotFound('page not found')

    return dict(village=village)

#TODO: OAuth Authorization for this endpoint
@view_config(route_name='api_village_list', renderer='json')
def api_village_list(request):
    return dict([(entity.identity, entity.to_dict())
                 for entity in VillageModel.objects.all()])


@view_config(route_name='api_village_join', renderer='json',
             request_method='POST')
def api_village_join(request):
    # TODO: pyramid でも動くようにする
    token = request.headers["authorization"].split()[1]
    user = AccessToken.objects.get(token=token).client_session.user

    game = Game.get_instance(request.POST['identity'])
    resident = game.join(user)

    return resident.to_dict()


@view_config(route_name='api_auth_token', renderer='json',
             request_method='POST')
def api_auth_token(request):
    try:
        client_id = request.POST['client_id']
        grant_type = request.POST['grant_type']
    except KeyError:
        raise InvalidRequestError('invalid request')

    if grant_type == GrantType.JWT_BEARER.value:
        try:
            assertion = request.POST['assertion']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = IdTokenAuthenticator(client_id)
        session = authenticator.validate(assertion)
    elif grant_type == GrantType.REFRESH_TOKEN.value:
        try:
            refresh_token = request.POST['refresh_token']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = RefreshTokenAuthenticator(client_id)
        session = authenticator.validate(refresh_token)
    else:
        raise UnsupportedGrantTypeError('unsupported grant type: {}'.format(grant_type))

    # TODO: use old refresh_token for grant_type=refresh_token
    access_token = session.generate_access_token()
    refresh_token = session.generate_refresh_token()

    return dict(
        access_token = access_token.token,
        token_type = 'bearer',
        expires_in = (access_token.expires_at - datetime.datetime.now()).seconds,
        refresh_token = refresh_token.token)


@view_config(context=Exception, renderer='json')
def handle_exception(exc, request):
    if not isinstance(exc, APIError):
        exc = ServerError(str(exc))
    request.response.status_int = exc.status_code
    return exc.to_dict()
