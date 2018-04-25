#!/usr/bin/env python

from FlclModbus.FlclModbusGateway import FlclModbusGateway
from twisted.internet import reactor, defer
import sys

@defer.inlineCallbacks
def _test(gtw):
    print 'do action'
    r = yield gtw.execute_action('test1', 'demo_1')
    print 'result:'
    print r
    print 'action done'
    try:
        reactor.stop()
        sys.exit(0)
    except:
        pass


if __name__ == "__main__":
    gtw=FlclModbusGateway('gateway.conf', 'actions.conf')
    print 'gateway created'
    reactor.callWhenRunning(_test, gtw)
    reactor.run()

