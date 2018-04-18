#!/usr/bin/env python

'''
'''

import FlclModbus.FlclModbusFactory as factory
import FlclModbus.FlclModbusComFactory as com_factory
from FlclModbus.FlclModbusRegister import *
import logging
from datetime import datetime
from pymodbus.server.sync import StartTcpServer
from pymodbus.server.sync import StartUdpServer
from pymodbus.server.sync import StartSerialServer


class PlcClient(object):

    registers=[]
    client=None


    def __init__(self, client):
        self.client=client
        registers=factory.make_register_table()


    def add_register(self, reg):
        if reg is not None:
            registers[reg.number]=reg


    def start_com(self):
        try:
            self.client.connect()
        except Exception as e:
            msg='{} Error starting modbus client: {}'\
                ''.format(datetime.now(), str(e.args).strip('(),\"'))
            logging.warning(result.get('msg'))


class ModbusComMaker(object):

    @staticmethod
    def read_one(plc, register):
        pass


    @staticmethod
    def write_one(plc, register):
        pass


    @staticmethod
    def read_multi(plc, registers):
        pass


    @staticmethod
    def write_multi(plc, registers):
        pass


class VirtualPlc(object):

    def __init__(self, config):
        # TODO: implement modbus server
        print 'Not implemented yet!'
