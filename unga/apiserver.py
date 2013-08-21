""" api server """
from twisted.internet import reactor, protocol
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template, g

app = Flask(__name__)
app.debug = True

@app.route("/")
def index():
    return "hello world"

wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), app)
wsgi_app = Site(wsgi_resource)


if __name__ == "__main__":
    reactor.listenTCP(8000, wsgi_app)
    reactor.run()
