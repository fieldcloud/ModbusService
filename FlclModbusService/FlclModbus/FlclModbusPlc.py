#!/usr/bin/env python

'''
Module used to manage communication from and to PLCs

'''

import FlclModbus.FlclModbusFactory as factory
import FlclModbus.FlclModbusComFactory as com_factory
from FlclModbus.FlclModbusRegister import *
import FlclModbus.FlclModbusRegister.ModbusRegisterFormatter as formatter
from FlclModbus.util import sleep
import logging
from datetime import datetime
from pymodbus.server.sync import StartTcpServer
from pymodbus.server.sync import StartUdpServer
from pymodbus.server.sync import StartSerialServer
from twisted.internet.defer import inlineCallbacks

class PlcClient(object):

    '''
       Manage modbus communication
    '''

    registers=[]
    client=None


    def __init__(self, client):
        
        self.client=client
        registers=factory.make_register_table()


#------------------------------------------------------------------------------#
# Registers methods                                                            #
#------------------------------------------------------------------------------#
    def add_register(self, reg):
        '''
            Add a specific register to the list
            :param reg: Register to add to plc
            :type reg: ModbusRegister  
        '''
        if reg is not None:
            self.registers[reg.number]=reg


    def get_register(self, number):
        '''
            Return specific register identified with his position number
            :param number: modbus number
            :type number: int
            :return: register at number position
            :rtype: ModbusRegister
        '''
        return self.registers.get(str(number))

#------------------------------------------------------------------------------#
# Modbus communication methods                                                 #
#------------------------------------------------------------------------------#
    def read_one(number):
        '''
            Load data from modbus plc in register, store in dedicated register
            & return specific register
            :param number: modbus number
            :type number: int
            :return: updated register
            :rtype: Modbus register
        '''
        try:
            reg = self.get_register(number)
            self.client.connect()
            desc = reg.get_type_description()
            method_name = desc.get('read_one')
            method = getattr(self.client, method_name)
            rr = method(reg.address, 1, unit=reg.unit)
            if rr.function_code<=80:
                v = rr.registers[0]
            else:
                v = 0
            reg.value=v
            self.client.close()
        except Exception as e:
            print e.args
            reg=None
        return reg


    def write_one(number, value):
        '''

        '''
        try:
            reg = self.get_register(number)
            self.client.connect()
            desc = reg.get_type_description()
            method_name = desc.get('write_one')
            method = getattr(self.client, method_name)
            rr = method(reg.address, value)
            self.client.close()
        except Exception as e:
            print e.args
        return self.read_one(number)


    def read_multi(first, nb):
        list=[]
        try:
            reg = self.get_register(first)
            self.client.connect()
            desc = reg.get_type_description()
            method_name = desc.get('read_multi')
            method = getattr(self.client, method_name)
            rr = method(reg.address, nb, unit=reg.unit)
            for i in range(0, nb):
                reg = self.get_register(first+i)
                if rr.function_code<=80:
                    v = rr.registers[i]
                else:
                    v = 0
                reg.value=v
                list.append(reg)
            self.client.close()
        except Exception as e:
            print e.args
        return list


    def write_multi(start, values):
        list=[]
        for i in (0, len(values)):
            list.append(self.write_one((start+i), values[i]))
        return list

#------------------------------------------------------------------------------#
# Asynchronous methods                                                         #
#------------------------------------------------------------------------------#
    @inlineCallbacks
    def wait(self, delay):
        yield sleep(delay)


#------------------------------------------------------------------------------#
# Direct use methods                                                           #
#------------------------------------------------------------------------------#
    def read_simple_int(self, number):
        r=self.read_one(number)
        return formatter.make_int_from_register(r)


    def write_simple_int(self, number, val):
        r=self.write_one(number, val)
        return formatter.make_int_from_register(r)

        

class VirtualPlc(object):

    def __init__(self, config):
        # TODO: implement modbus server
        print 'Not implemented yet!'
