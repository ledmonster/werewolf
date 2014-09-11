# -*- coding: utf-8 -*-
""" api server """
import datetime

from pyramid.view import view_config

from werewolf.domain.game.models import *
from werewolf.domain.user.models import *
from werewolf.domain.user.exception import *


#TODO: OAuth Authorization for this endpoint
@view_config(route_name='api_village_list', renderer='json')
def api_village_list(context, request):
    repo_village = context.repos['village']
    return {
        "villages": [entity.to_dict() for entity in repo_village.find()]
        }


@view_config(route_name='api_village_detail', renderer='json')
def api_village_detail(context, request):
    repo_village = context.repos['village']
    identity = request.matchdict.get('identity')
    try:
        village = repo_village.get_entity(identity=identity)
    except ValueError:
        raise NotFoundError('page not found')

    return {"village": village.to_dict()}


@view_config(route_name='api_village_join', renderer='json',
             request_method='POST')
def api_village_join(context, request):
    user = context.repos['user'].get(request.authenticated_userid)
    game = GameService(context, request.POST['identity'])
    resident = game.join(user)

    return resident.to_dict()


@view_config(route_name='api_auth_token', renderer='json',
             permission='everyone', request_method='POST')
def api_auth_token(context, request):
    try:
        client_id = request.POST['client_id']
        grant_type = request.POST['grant_type']
    except KeyError:
        raise InvalidRequestError('invalid request')

    if request.registry.settings["oauth2.client_id"] != client_id:
        raise InvalidClientError('Invalid client_id: {}'.format(client_id))

    if grant_type == GrantType.JWT_BEARER.value:
        try:
            assertion = request.POST['assertion']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = IdTokenAuthenticator(context, client_id)
        session = authenticator.validate(assertion)
    elif grant_type == GrantType.REFRESH_TOKEN.value:
        try:
            refresh_token = request.POST['refresh_token']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = RefreshTokenAuthenticator(context, client_id)
        session = authenticator.validate(refresh_token)
    else:
        raise UnsupportedGrantTypeError('unsupported grant type: {}'.format(grant_type))

    # TODO: use old refresh_token for grant_type=refresh_token
    access_token = session.generate_access_token()
    refresh_token = session.generate_refresh_token()
    context.repos['access_token'].save(access_token)
    context.repos['refresh_token'].save(refresh_token)

    return dict(
        access_token = access_token.token,
        token_type = 'bearer',
        expires_in = (access_token.expires_at - datetime.datetime.now()).seconds,
        refresh_token = refresh_token.token)


@view_config(context=Exception, renderer='json')
def handle_exception(exc, request):
    if isinstance(exc, HTTPException):
        request.response.status_int = exc.code
        return ServerError(str(exc)).to_dict()
    if not isinstance(exc, APIError):
        exc = ServerError(str(exc))
    request.response.status_int = exc.status_code
    return exc.to_dict()
