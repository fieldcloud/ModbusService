#!/usr/bin/env python

'''


'''

HOLDING_REGISTER=0X00
COIL_REGISTER=0X01
INPUT_REGISTER=0X02
DISCRETE_INPUT_REGISTER=0X03

REGISTER_TYPES = {
    'coil': {
        'offset':1,
        'read_one': 'read_coils',
        'write_one': 'write_coil',
        'read_multi': 'read_coils',
        'write_multi': 'write_coils'
    },
    'discrete_input': {
        'offset':10001,
        'read_one': 'read_discrete_inputs',
        'write_one': None,
        'read_multi': 'read_discrete_inputs',
        'write_multi': None
    },
    'input': {
        'offset':30001,
        'read_one': 'read_input_registers',
        'write_one': None,
        'read_multi': 'read_input_registers',
        'write_multi': None
    },
    'holding': {
        'offset':40001,
        'read_one': 'read_holding_registers',
        'write_one': 'write_register',
        'read_multi': 'read_holding_registers',
        'write_multi': 'write_registers'
    }
}


class ModbusRegister(object):

    self.number=0

    def __init__(self, type, address, value=0, unit=0x01):
        self.type=type
        self.address=address
        self.value=value
        self.unit=unit
        self.bin_value= str(value) if value<=1 else bin(value>>1)+str(value&1)
        self.bin_value= self.bin_value.lstrip('0b')


    def set_value(self, value):
        self.bin_value= str(value) if value<=1 else bin(value>>1)+str(value&1)
        self.bin_value= self.bin_value.lstrip('0b')
        self.value=value


    def get_bit_at(self,pos=0):
        if pos >= 0 and pos <16:
            return int(self.bin_value[abs(pos-15)])
        else:
            return -1


    def get_type_description(self):
        d={}
        if self.type is not None:
            if self.type == HOLDING_REGISTER:
                d=REGISTER_TYPES.get('holding')
            elif self.type == COIL_REGISTER:
                d=REGISTER_TYPES.get('coil')
            elif self.type == INPUT_REGISTER:
                d=REGISTER_TYPES.get('input')
            elif self.type == DISCRETE_INPUT_REGISTER:
                d=REGISTER_TYPES.get('discrete_input')
        return d


class ModbusReadWriteRegister(ModbusRegister):


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


class ModbusCoilRegister(ModbusReadWriteRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister(self, COIL_REGISTER, address, value=value, unit=unit)
        self.number=self.address+REGISTER_TYPES.get('coil').get('offset')


    def get_type_description(self, type):
        return REGISTER_TYPES.get('coil')


class ModbusDiscreteInputRegister(ModbusRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister(self, DISCRETE_INPUT_REGISTER, address, value=value,
                       unit=unit)
        self.number=self.address+REGISTER_TYPES.get('discrete_input')
                                                    .get('offset')


    def get_type_description(self):
        return REGISTER_TYPES.get('discrete_input')


class ModbusInputRegister(ModbusRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister(self, INPUT_REGISTER, address, value=value, unit=unit)
        self.number=self.address+REGISTER_TYPES.get('input').get('offset')


    def get_type_description(self):
        return REGISTER_TYPES.get('input')


class ModbusHoldingRegister(ModbusReadWriteRegister):


    def __init__(self, address, value=0, unit=0x01):
        ModbusRegister(self, HOLDING_REGISTER, address, value=value, unit=unit)
        self.number=self.address+REGISTER_TYPES.get('holding').get('offset')

    def get_type_description(self):
        return REGISTER_TYPES.get('holding')


class ModbusRegisterFormatter(object):


    @staticmethod
    def set_int_in_register(value, register):
        register.set_value(value)
        return register


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
        bs='0b'
        for reg in registers:
            bs='{}{}'.format(bs, reg.bin_value)
        return int(bs, 2)


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
