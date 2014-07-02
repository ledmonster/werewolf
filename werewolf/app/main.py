""" werewolf server """
import os

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"

from django.conf import settings
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line

from werewolf.app.api import app as flask_app
from werewolf.app.admin.wsgi import application as django_admin_app
from werewolf.app.websocket import SocketHandler

define("port", default=5000, help="run on the given port", type=int)

def main():
    app = Application([
        (r'/websocket', SocketHandler),
        ('/admin/.*', FallbackHandler, dict(fallback=WSGIContainer(django_admin_app))),
        ('/static/admin/.*', FallbackHandler, dict(fallback=WSGIContainer(django_admin_app))),
        ('.*', FallbackHandler, dict(fallback=WSGIContainer(flask_app))),
    ], debug=settings.DEBUG)
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    parse_command_line()
    main()
