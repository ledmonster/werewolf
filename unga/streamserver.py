""" stream server """
from twisted.internet import reactor, protocol
from twisted.protocols import basic


class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        for c in self.factory.clients:
            c.sendLine("<{}> {}".format(self.transport.getHost(), line))

class PubFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()

    def buildProtocol(self, addr):
        return PubProtocol(self)


if __name__ == "__main__":
    reactor.listenTCP(1025, PubFactory())
    reactor.run()
