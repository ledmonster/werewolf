""" api server """
import datetime

from twisted.internet import reactor, protocol
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template, g, abort, jsonify, request, Response

from unga.auth import IdTokenAuthenticator, RefreshTokenAuthenticator

app = Flask(__name__)
app.debug = True

GRANT_TYPE_JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
GRANT_TYPE_REFRESH_TOKEN = "refresh_token"

@app.route('/v1/auth/token', methods=['POST'])
def auth_token():
    try:
        client_id = request.form['client_id']
        grant_type = request.form['grant_type']
    except KeyError:
        return Response('invalid_request', status=400)

    if grant_type == GRANT_TYPE_JWT_BEARER:
        try:
            assertion = request.form['assertion']
        except KeyError:
            return Response('invalid_request', status=400)

        authenticator = IdTokenAuthenticator(client_id)
        session = authenticator.validate(assertion)
    elif grant_type == GRANT_TYPE_REFRESH_TOKEN:
        try:
            refresh_token = request.form['refresh_token']
        except KeyError:
            return Response('invalid_request', status=400)

        authenticator = RefreshTokenAuthenticator(client_id)
        session = authenticator.validate(refresh_token)
    else:
        return Response('unsupported_grant_type', status=400)

    # TODO: use old refresh_token for grant_type=refresh_token
    access_token = session.generate_access_token()
    refresh_token = session.generate_refresh_token()

    res = dict(
        access_token = access_token.token,
        token_type = 'bearer',
        expires_in = (access_token.expires_at - datetime.datetime.now()).seconds,
        refresh_token = refresh_token.token)

    return jsonify(res)

wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), app)
wsgi_app = Site(wsgi_resource)


if __name__ == "__main__":
    reactor.listenTCP(8000, wsgi_app)
    reactor.run()
