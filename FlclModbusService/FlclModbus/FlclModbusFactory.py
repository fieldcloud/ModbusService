#!/usr/bin/env python

'''
   Methods used to create modbus components

'''

from pymodbus.client.sync import *
from FlclModbus.FlclModbusPlc import PlcClient
from FlclModbus.FlclModbusRegister import *
import FlclModbus.FlclModbusRegister as reg

MODBUS_TCP_CLIENT=0x00
MODBUS_UDB_CLIENT=0x01
MODBUS_SERIAL_CLIENT=0x02


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
        plc=PlcClient(client)
        for r in plc_conf.get('registers'):
            plc.add_register(create_register(r.get('type'),
                                             r.get('address'),
                                             value=r.get('value'))
    return plc


def create_register(type, address, value=0):
    if value is None:
        value == 0
    if type==reg.HOLDING_REGISTER:
        return ModbusHoldingRegister(address, value)
    elif type==reg.COIL_REGISTER:
        return ModbusCoilRegister(address, value)
    elif type==reg.INPUT_REGISTER:
        return ModbusInputRegister(address, value)
    elif type==reg.DISCRETE_INPUT_REGISTER:
        return ModbusDiscreteInputRegister(address, value)
    else:
        return None


def make_register_table():
    registers=[]
    for i in range(0, 9999):
        reg=ModbusCoilRegister(i)
        registers.append({str(reg.number):reg})
    for i in range(0, 9999):
        reg=ModbusDiscreteInputRegister(i)
        registers.append({str(reg.number):reg})
    for i in range(0, 9999):
        reg=ModbusInputRegister(i)
        registers.append({str(reg.number):reg})
    for i in range(0, 9999):
        reg=ModbusHoldingRegister(i)
        registers.append({str(reg.number):reg})
