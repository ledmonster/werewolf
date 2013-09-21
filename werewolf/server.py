""" werewolf server """
import os

# initialize django
os.environ["DJANGO_SETTINGS_MODULE"] = "werewolf.settings"

from twisted.internet import reactor
from werewolf.apiserver import wsgi_app
from werewolf.streamserver import stream_app

def main():
    reactor.listenTCP(1025, stream_app)
    reactor.listenTCP(8000, wsgi_app)
    reactor.run()

if __name__ == "__main__":
    main()
