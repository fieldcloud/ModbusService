#!/usr/bin/env python

'''
Module used to manage communication from and to PLCs

'''

import FlclModbus.FlclModbusFactory as factory
import FlclModbus.FlclModbusComFactory as com_factory
from FlclModbus.FlclModbusRegister import *
import FlclModbus.FlclModbusRegister.ModbusRegisterFormatter as formatter
from FlclModbus.util import sleep, int_to_bytes, bytes_to_int
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
    id='demo'


    def __init__(self, client, id):
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
    def read_one(self, params):
        '''
            Load data from modbus plc in register, store in dedicated register
            & return specific register
            :param paramsr: dict containing parameters (number)
            :type params: dict
            :return: list of register value
            :rtype: list
        '''
        list=[]
        try:
            number=params.get('number')
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
        return list.append(self._make_resp_from_register(reg))


    def write_one(self, params):
        '''
            Write value to Plc, Load data from modbus plc in register, 
            store in dedicated register & return specific register
            :param paramsr: dict containing parameters (number, value)
            :type params: dict
            :return: list of register value
            :rtype: list
        '''
        try:
            number=params.get('number')
            value=params.get('value')
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


    def read_multi(self, params):
        '''
            Load data from modbus plc in registers lis, 
            store in dedicated registers & return specific registers
            :param paramsr: dict containing parameters (start, count)
            :type params: dict
            :return: list of register value
            :rtype: list
        '''
        list=[]
        try:
            first=params.get('start')
            nb=params.get('count')
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
                list.append(self._make_resp_from_register(reg))
            self.client.close()
        except Exception as e:
            print e.args
        return list


    def write_multi(self, params):
        '''
            Write value to Plc, Load data from modbus plc in register, 
            store in dedicated register & return specific register
            :param paramsr: dict containing parameters (start, value, count)
            :type params: dict
            :return: list of register value
            :rtype: list
        '''
        list=[]
        start=params.get('start')
        value=params.get('value')
        nb=params.get('count')
        values=int_to_bytes(value, nb)
        for i in (0, nb):
            r=self.write_one((start+i), values[i])
            if len(r] = 1:
               list.append(r[0])
        return list


    def _make_resp_from_register(self, register):
        resp = {}
        resp['number']=register.number
        resp['value']=register.value


#------------------------------------------------------------------------------#
# Asynchronous methods                                                         #
#------------------------------------------------------------------------------#
    @inlineCallbacks
    def wait(self, params):
        delay=params.get('delay')
        yield sleep(delay)
        yield returnValue({})


#------------------------------------------------------------------------------#
# Direct use methods                                                           #
#------------------------------------------------------------------------------#
    def read_int(self, params):
        r=self.read_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_int_from_register(reg))
        return r


    def read_int_multi(self, params):
        r=self.read_multi(params)
        reg_list=[]
        for resp in r:
            reg=self.get_register(resp.get('number'))
            reg_list.append(reg)
        v={}
        v['name']=r[params.get('name')]
        v['value']=formatter.make_int_from_list(reg_list)
        r.append(v)
        return r


    def read_float(self, params):
        coef=params.get('coef')
        r=self.read_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_float_from_register(reg, coef)
        return r


    def read_float_multi(self, params):
        coef=params.get('coef')
        nb=params.get('nb')
        r=self.read_multi(params)
        reg_list=[]
        for resp in r:
            reg=self.get_register(resp.get('number'))
            reg_list.append(reg)
        v={}
        v['name']=r[params.get('name')]
        v['value']= formatter.make_float_from_list(r, nb, coef)
        r.append(v)
        return r


    def read_bool(self, params):
        r=self.read_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_boolean_from_register(reg)
        return r


    def read_bool_at(self, params):
        pos=params.get('pos')
        r=self.read_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_boolean_from_bit(reg, pos)
        return r


    def write_int(self, params):
        r=self.write_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_int_from_register(reg)
        return r


    def write_int_multi(self, params):
        r=self.write_multi(params)
        reg_list=[]
        for resp in r:
            reg=self.get_register(resp.get('number'))
            reg_list.append(reg)
        v={}
        v['name']=r[params.get('name')]
        v['value']= formatter.make_int_from_list(r)
        r.append(v)
        return r


    def write_float(self, params):
        val=params.get('val')
        coef=params.get('coef')
        val = int(val*coef)
        params['val']=val
        r=self.write_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_float_from_register(reg, coef)
        return r


    def write_float_multi(self, params):
        val=params.get('val')
        val = int(val*coef)
        params['val']=val
        r=self.write_multi(params)
        reg_list=[]
        for resp in r:
            reg=self.get_register(resp.get('number'))
            reg_list.append(reg)
        v={}
        v['name']=r[params.get('name')]
        v['value']=formatter.make_int_from_list(r)
        r.append(v)
        return r


    def write_bool(self, params):
        number=params.get('number')
        val=params.get('val')
        r=self.get_register(number)
        r=formatter.set_bool_in_register(val, r)
        params['val']=val
        r=self.write_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_int_from_register(r)
        return r


    def write_bool_at(self, params):
        number=params.get('number')
        val=params.get('val')
        pos=params.get('pos')
        r=self.get_register(number)
        r=formatter.set_bool_in_register_at(val, r, pos)
        params['val']=val
        r=self.write_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_int_from_register(r)
        return r


class VirtualPlc(object):

    def __init__(self, config):
        # TODO: implement modbus server
        print 'Not implemented yet!'
