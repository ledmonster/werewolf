""" stream server """
from twisted.internet import reactor, protocol
from twisted.protocols import basic


class StreamProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        for c in self.factory.clients:
            c.sendLine("<{}> {}".format(self.transport.getHost(), line))

class StreamFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()

    def buildProtocol(self, addr):
        return StreamProtocol(self)

stream_app = StreamFactory()


if __name__ == "__main__":
    reactor.listenTCP(1025, stream_app)
    reactor.run()
