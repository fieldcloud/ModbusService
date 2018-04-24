#!/usr/bin/env python

from FlclModbus.FlclModbusGateway import FlclModbusGateway

if __name__ == "__main__":
    gtw=FlclModbusGateway('gateway.conf', 'actions.conf')
    gtw.run()
    gtw.execute_action('test1', 'demo_1')

