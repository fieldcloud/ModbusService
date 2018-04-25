#!/usr/bin/env python

from FlclModbus.FlclModbusGateway import FlclModbusGateway
from twisted.internet import reactor, defer

@defer.inlineCallbacks
def _test(gtw):
    print 'do action'
    r = yield gtw.execute_action('test1', 'demo_1')
    print r
    print 'action done'


if __name__ == "__main__":
    gtw=FlclModbusGateway('gateway.conf', 'actions.conf')
    print 'gateway created'
    reactor.callWhenRunning(_test, gtw)
    reactor.run()

