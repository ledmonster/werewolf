""" werewolf server """
import os

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"

from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from werewolf.apiserver import app as flask_app
from werewolf.websocketserver import SocketHandler

def main():
    app = Application([
        (r'/websocket', SocketHandler),
        ('.*', FallbackHandler, dict(fallback=WSGIContainer(flask_app))),
    ])
    http_server = HTTPServer(app)
    http_server.listen(8000)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
