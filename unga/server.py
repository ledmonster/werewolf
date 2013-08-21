""" unga server """
from twisted.internet import reactor
from unga.apiserver import wsgi_app
from unga.streamserver import stream_app

def main():
    reactor.listenTCP(1025, stream_app)
    reactor.listenTCP(8000, wsgi_app)
    reactor.run()

if __name__ == "__main__":
    main()
