#!/usr/bin/env python

'''


'''

from FlclModbus.util import int_to_bytes, bytes_to_int


HOLDING_REGISTER='holding'
COIL='coil'
INPUT_REGISTER='input'
DISCRETE_INPUT='discrete_input'

REGISTER_TYPES = {
    COIL: {
        'offset':1,
        'read_one': 'read_coils',
        'write_one': 'write_coil',
        'read_multi': 'read_coils',
        'write_multi': 'write_coils'
    },
    DISCRETE_INPUT: {
        'offset':10001,
        'read_one': 'read_discrete_inputs',
        'read_multi': 'read_discrete_inputs',
    },
    INPUT_REGISTER: {
        'offset':30001,
        'read_one': 'read_input_registers',
        'read_multi': 'read_input_registers',
    },
    HOLDING_REGISTER: {
        'offset':40001,
        'read_one': 'read_holding_registers',
        'write_one': 'write_register',
        'read_multi': 'read_holding_registers',
        'write_multi': 'write_registers'
    }
}


class ModbusData(object):


    def __init__(self, type, address, value, unit=0x01):
        self.type=type
        self.address=address
        self.value=value
        self.unit=unit
        self.number=self.address+REGISTER_TYPES.get(type).get('offset')


    def get_type_description(self):
        return REGISTER_TYPES.get(self.type)


    def get_number(self):
        return self.number


class ModbusRegister(ModbusData):


    def __init__(self, type, address, value=0, unit=0x01):
        ModbusData.__init__(self, type, address, value, unit=0x01)
        self.bin_value= str(value) if value<=1 else bin(value>>1)+str(value&1)
        self.bin_value= self.bin_value.lstrip('0b')


    def get_bit_at(self,pos=0):
        if pos >= 0 and pos <16:
            return int(self.bin_value[abs(pos-15)])
        else:
            return -1


    def set_value(self, value):
        self.bin_value= str(value) if value<=1 else bin(value>>1)+str(value&1)
        self.bin_value= self.bin_value.lstrip('0b')
        self.value=value



class ModbusSingle(ModbusData):


    def __init__(self, type, address, value=False, unit=0x01):
        ModbusData.__init__(self, type, address, value, unit=0x01)


class ModbusCoil(ModbusSingle):


    def __init__(self, address, value=False, unit=0x01):
        ModbusSingle.__init__(self, COIL, address,
                                          value=value, unit=unit)


    def set_value(self, value):
        self.value=value


class ModbusDiscreteInput(ModbusSingle):


    def __init__(self, address, value=False, unit=0x01):
        ModbusSingle.__init__(self, DISCRETE_INPUT, address,
                                value=value, unit=unit)


class ModbusInputRegister(ModbusRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister.__init__(self, INPUT_REGISTER, address,
                                    value=value, unit=unit)


class ModbusHoldingRegister(ModbusRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister.__init__(self, HOLDING_REGISTER, address,
                                      value=value, unit=unit)


    def set_bit_value(self, pos, val):
        p = 0
        prev = self.bin_value
        new = ''
        while p < 16:
            if p == abs(pos-15):
                v = val
            else:
                v = self.bin_value[p]
            new = '{}{}'.format(new,v)
            p=p+1
        self.bin_value = new
        self.value = int(new,2)


class ModbusRegisterFormatter(object):


    @staticmethod
    def set_int_in_register(value, register):
        register.set_value(value)
        return register


    @staticmethod
    def set_int_in_register_list(value, registers):
        il=int_to_bytes(value, len(registers))
        for i in range(0, len(registers)):
            registers[i].value=il[i]
        return registers


    @staticmethod
    def set_float_in_register(value, register, coef):
        val=int(value*coef)
        return ModbusRegisterFormatter.set_int_in_register(val, register)


    @staticmethod
    def set_float_in_register_list(value, registers, coef):
        val=int(value*coef)
        return ModbusRegisterFormatter.set_int_in_register_list(val, registers)


    @staticmethod
    def set_bool_in_register(value, register):
        if value==True:
            register.set_value(0x01)
        else:
            register.set_value(0x00)
        return register


    @staticmethod
    def set_bool_in_register_at(value, register, pos):
        if value==True:
            v=1
        else:
            v=0
        try:
            register.set_bit_value(pos, v)
        except:
            pass
        return register


    @staticmethod
    def make_int_from_register(register):
        return int(register.value)


    @staticmethod
    def make_int_from_list(registers):
        l=[]
        for reg in registers:
            l.append(reg.value)
        return bytes_to_int(l)


    @staticmethod
    def make_float_from_register(register, coef):
        return float(register.value)/float(coef)


    @staticmethod
    def make_float_from_list(registers, coef):
        fv=float(ModbusRegisterFormatter.make_int_from_list(registers))
        return fv /float(coef)


    @staticmethod
    def make_boolean_from_bit(register, pos):
        v=register.get_bit_at(pos)
        return v==1


    @staticmethod
    def make_boolean_from_register(register):
        return register.value>0
