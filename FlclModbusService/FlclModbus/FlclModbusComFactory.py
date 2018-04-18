#!/usr/bin/env python

'''
   Methods used to create modbus components

'''

from pymodbus.client.sync import *

MODBUS_TCP_CLIENT=0x00
MODBUS_UDB_CLIENT=0x01
MODBUS_SERIAL_CLIENT=0x02


def create_client(conf):
    client = None
    if conf is not None:
        if conf.get('type')==MODBUS_TCP_CLIENT:
            client=ModbusTcpClient(conf.get('url'), conf.get('port'))
        elif conf.get('type')==MODBUS_UDP_CLIENT:
            client=ModbusUdpClient(conf.get('url'), conf.get('port'))
        elif conf.get('type')==MODBUS_SERIAL_CLIENT:
            client=ModbusSerialClient(conf.get('method'))
    return client

