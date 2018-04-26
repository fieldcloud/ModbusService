#!/usr/bin/env python

'''
Module used to manage communication from and to PLCs

'''

from FlclModbus.FlclModbusRegister import *
from FlclModbus.FlclModbusRegister import ModbusRegisterFormatter as formatter
from FlclModbus.util import sleep, int_to_bytes, bytes_to_int
import logging
from datetime import datetime
from pymodbus.server.sync import StartTcpServer
from pymodbus.server.sync import StartUdpServer
from pymodbus.server.sync import StartSerialServer
from pymodbus.client.sync import *

from twisted.internet.defer import inlineCallbacks, returnValue

__version__='0.1.0'


MODBUS_TCP_CLIENT='tcp'
MODBUS_UDP_CLIENT='udp'
MODBUS_SERIAL_CLIENT='serial'


def create_client(com_conf):
    client = None
    if com_conf is not None:
        if com_conf.get('type')==MODBUS_TCP_CLIENT:
            client=ModbusTcpClient(com_conf.get('url'),
                                   port=com_conf.get('port'))
        elif com_conf.get('type')==MODBUS_UDP_CLIENT:
            client=ModbusUdpClient(com_conf.get('url'),
                                   port=com_conf.get('port'))
        elif com_conf.get('type')==MODBUS_SERIAL_CLIENT:
            client=ModbusSerialClient(method=com_conf.get('method'))
    return client


def create_plc_client(plc_conf):
    plc=None
    if plc_conf is not None:
        client = create_client(plc_conf.get('plc_com'))
        plc=PlcClient(client, plc_conf.get('id'))
        for r in plc_conf.get('registers'):
            plc.add_register(create_register(r.get('type'),
                                             r.get('address'),
                                             value=r.get('value')))
    return plc


def create_register(type, address, value=0):
    if value is None:
        value = 0
    if type==HOLDING_REGISTER:
        return ModbusHoldingRegister(address, value=value)
    elif type==COIL:
        return ModbusCoil(address, value=value)
    elif type==INPUT_REGISTER:
        return ModbusInputRegister(address, value=value)
    elif type==DISCRETE_INPUT:
        return ModbusDiscreteInput(address, value=value)
    else:
        return None


def make_register_table():
    registers={}
    for i in range(0, 9999):
        reg=ModbusCoil(i)
        registers[str(reg.get_number())]=reg
    for i in range(0, 9999):
        reg=ModbusDiscreteInput(i)
        registers[str(reg.get_number())]=reg
    for i in range(0, 9999):
        reg=ModbusInputRegister(i)
        registers[str(reg.get_number())]=reg
    for i in range(0, 9999):
        reg=ModbusHoldingRegister(i)
        registers[str(reg.get_number())]=reg
    return registers


class PlcClient(object):

    '''
       Manage modbus communication
    '''

    registers={}
    client=None
    id='demo'


    def __init__(self, client, id):
        '''
            Initialize PlcClient creation & create registers list
            :param client: Synchronous modbus client from pymongo
            :type client: pymongo sync client
        '''
        self.client=client
        self.registers=make_register_table()
        self.id=id


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
        reg=None
        for k, v in self.registers.iteritems():
            if str(number) == k:
                reg = v
        return reg

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
            print 'Start reading one'
            number=params.get('number')
            reg = self.get_register(number)
            self.client.connect()
            desc = reg.get_type_description()
            method_name = desc.get('read_one')
            method = getattr(self.client, method_name)
            br = isinstance(reg, ModbusCoil) == True
            br = br or isinstance(reg, ModbusDiscreteInput) == True
            print br
            rr = method(reg.address, 1, unit=reg.unit)
            if br == True:
                if rr.function_code<=80:
                    reg.value= rr.bits[0]
                else:
                    reg.value=-1
                return reg
            else:
                print rr
                if rr.function_code<=80:
                    v = rr.registers[0]
                else:
                    v = -1
                reg.value=v
            print reg
            self.client.close()
        except Exception as e:
            print 'error reading one'
            print e.args
            reg=None
        if reg is not None:
            resp=self._make_resp_from_register(reg)
            if resp is not None:
                list.append(resp)
        print 'End reading one with result:'
        print list
        return list


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
            writable=isinstance(reg, ModbusCoil)
            writable=writable or isinstance(reg, ModbusHoldingRegister)
            if writable == True:
                reg.set_value(value)
                self.client.connect()
                desc = reg.get_type_description()
                method_name = desc.get('write_one')
                method = getattr(self.client, method_name)
                if isinstance(reg, ModbusHoldingRegister):
                    rr = method(reg.address, value, unit=0x01)
                else:
                    rr = method(reg.address, [value], unit=0x01)
                self.client.close()
        except Exception as e:
            print e.args
        return self.read_one(params)


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
            br = isinstance(reg, ModbusCoil) == True
            br = br or isinstance(reg, ModbusDiscreteInput) == True
            if rr.function_code<=80:
                if br == True:
                    l=rr.bits
                else:
                    l=rr.registers
            else:
                l=[0]*nb
            for i in range(0, nb):
                reg = self.get_register(first+i)
                reg.value=l[i]
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
        values=params.get('values')
        try:
            writable=isinstance(reg, ModbusCoil)
            writable=writable or isinstance(reg, ModbusHoldingRegister)
            if writable == True:
                reg = self.get_register(first)
                self.client.connect()
                desc = reg.get_type_description()
                method_name = desc.get('write_multi')
                method = getattr(self.client, method_name)
                rr = method(reg.address, values, unit=reg.unit)
                self.client.close()
        except Exception as e:
            print e.args
        return self.readmulti(params)


    def _make_resp_from_register(self, register):
        resp = {}
        resp['number']=register.number
        resp['value']=register.value
        return resp


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
        print 'Start reading int'
        r=self.read_one(params)
        for resp in r:
            reg=self.get_register(resp.get('number'))
            resp['value'] = formatter.make_int_from_register(reg)
        print 'End reading with result:'
        print r
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
