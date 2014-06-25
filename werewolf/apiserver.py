""" api server """
import datetime

from flask import Flask, render_template, g, abort, jsonify, request, Response

from werewolf import settings
from werewolf.domain import Game
from werewolf.models import *
from werewolf.user.models import *
from werewolf.exception import *


app = Flask(__name__)
app.debug = True

GRANT_TYPE_JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
GRANT_TYPE_REFRESH_TOKEN = "refresh_token"

@app.route('/')
def index():
    return render_template('index.html', settings=settings)


@app.route('/village/list')
def village_list():
    return render_template('village/list.html', settings=settings)


@app.route('/village/<identity>')
def village_detail(identity):
    try:
        village = VillageModel.objects.get(identity=identity)
    except VillageModel.DoesNotExist:
        raise NotFoundError('page not found')

    return render_template('village/detail.html', village=village,
                           settings=settings)

#TODO: OAuth Authorization for this endpoint
@app.route('/api/v1/village/list')
def api_village_list():
    village_list = dict([(entity.identity, entity.to_dict())
                         for entity in VillageModel.objects.all()])
    return jsonify(village_list)


@app.route('/api/v1/village/join', methods=['POST'])
def api_village_join():
    token = request.headers["authorization"].split()[1]
    user = AccessToken.objects.get(token=token).client_session.user

    game = Game.get_instance(request.form['identity'])
    resident = game.join(user)

    return jsonify(resident.to_dict())


@app.route('/api/v1/auth/token', methods=['POST'])
def api_auth_token():
    try:
        client_id = request.form['client_id']
        grant_type = request.form['grant_type']
    except KeyError:
        raise InvalidRequestError('invalid request')

    if grant_type == GRANT_TYPE_JWT_BEARER:
        try:
            assertion = request.form['assertion']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = IdTokenAuthenticator(client_id)
        session = authenticator.validate(assertion)
    elif grant_type == GRANT_TYPE_REFRESH_TOKEN:
        try:
            refresh_token = request.form['refresh_token']
        except KeyError:
            raise InvalidRequestError('invalid request')

        authenticator = RefreshTokenAuthenticator(client_id)
        session = authenticator.validate(refresh_token)
    else:
        raise UnsupportedGrantTypeError('unsupported grant type: {}'.format(grant_type))

    # TODO: use old refresh_token for grant_type=refresh_token
    access_token = session.generate_access_token()
    refresh_token = session.generate_refresh_token()

    res = dict(
        access_token = access_token.token,
        token_type = 'bearer',
        expires_in = (access_token.expires_at - datetime.datetime.now()).seconds,
        refresh_token = refresh_token.token)

    return jsonify(res)

@app.errorhandler(Exception)
def handle_exception(error):
    if not isinstance(error, APIError):
        error = ServerError(str(error))
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    wsgi_app = WSGIContainer(app)
    http_server = HTTPServer(wsgi_app)
    http_server.listen(8000)
    IOLoop.instance().start()
