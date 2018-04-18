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

__version__='0.1.0'


class PlcClient(object):

    '''
       Manage modbus communication
    '''

    registers=[]
    client=None


    def __init__(self, client):
        '''
            Initialize PlcClient creation & create registers list
            :param client: Synchronous modbus client from pymongo
            :type client: pymongo sync client
        '''
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
    def read_one(self, number):
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


    def write_one(self, number, value):
        '''

        '''
        try:
            reg = self.get_register(number)
            reg.set_value(value)
            self.client.connect()
            desc = reg.get_type_description()
            method_name = desc.get('write_one')
            method = getattr(self.client, method_name)
            rr = method(reg.address, value)
            self.client.close()
        except Exception as e:
            print e.args
        return self.read_one(number)


    def read_multi(self, first, nb):
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


    def write_multi(self, start, value, nb):
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
    def read_int(self, number):
        r=self.read_one(number)
        return formatter.make_int_from_register(r)


    def read_int_multi(self, number, nb):
        r=self.read_multi(number, nb)
        return formatter.make_int_from_list(r)


    def read_float(self, number, coef):
        r=self.read_one(number)
        return formatter.make_float_from_register(r, coef)


    def read_float_multi(self, number, nb):
        r=self.read_multi(number, nb)
        return formatter.make_float_from_list(r, coef)


    def read_bool(self, number):        
        r=self.read_one(number)
        return formatter.make_boolean_from_register(r)


    def read_bool_at(self, number, pos):
        r=self.read_one(number)
        return formatter.make_boolean_from_bit(r, pos)


    def write_int(self, number, val):
        r=self.write_one(number, val)
        return formatter.make_int_from_register(r)


    def write_int_multi(self, number, val, nb):
        r=self.write_multi(number, val)
        return formatter.make_int_from_list(r)


    def write_float(self, number, val, coef):
        val = int(val*coef)
        r=self.write_one(number, val)
        return formatter.make_int_from_register(r)


    def write_float_multi(self, number, val, nb, coef):
        val = int(val*coef)
        r=self.write_multi(number, val)
        return formatter.make_int_from_list(r)


    def write_boolean(self, number, val):
        r=self.get_register(number)
        r=formatter.set_bool_in_register(val, r)
        r=self.write_one(number, r.value)
        return formatter.make_int_from_register(r)


    def write_boolean_at(self, number, val, pos):
        r=self.get_register(number)
        r=formatter.set_bool_in_register_at(val, r, pos)
        r=self.write_one(number, r.value)
        return formatter.make_int_from_register(r)


class VirtualPlc(object):

    def __init__(self, config):
        # TODO: implement modbus server
        print 'Not implemented yet!'
