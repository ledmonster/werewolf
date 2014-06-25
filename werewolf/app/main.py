""" werewolf server """
import os

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"

from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from werewolf import settings
from werewolf.app.api import app as flask_app
from werewolf.app.admin.wsgi import application as django_admin_app
from werewolf.app.websocket import SocketHandler

def main():
    app = Application([
        (r'/websocket', SocketHandler),
        ('/admin/.*', FallbackHandler, dict(fallback=WSGIContainer(django_admin_app))),
        ('/static/admin/.*', FallbackHandler, dict(fallback=WSGIContainer(django_admin_app))),
        ('.*', FallbackHandler, dict(fallback=WSGIContainer(flask_app))),
    ], debug=settings.DEBUG)
    http_server = HTTPServer(app)
    http_server.listen(5000)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
