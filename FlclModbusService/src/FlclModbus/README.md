# Modbus communication service

## Modbus devices


## Stepper

The stepper is in charge of executing actions.

## Action


### Description

An action is a succession of device/plcs elementaries actions.

### Modbus device/plc actions

#### Modbus level

Available:

* read_one => read one register and return value
* write_one => write value into register and return value
* read_multi => read list of registers and return values list
* write_multi => write list of values into registers and return values list


#### Asynchronous 

Available:

* wait => sleep while affected delay


#### Variables manipulation

Available :

* read_int => read value fom one register and return integer value
* read_int_multi => read values from several integers and return int value
* read_float => read value from one register and return float value
* read_float_multi => read values from several integers and return float value
* read_bool => read value fom one register and return boolean value
* read_bool_at => read value fom one register and return boolean value of one specific bit
* write_int => update register with int value and return integer value
* write_int_list => update register with int value and return integer values list
* write_float => update register with int value and return float value
* write_float_list => update register with float value and return float values list
* write_bool => update register with boolean value and return boolean value
* write_bool_at => update specific bit value in register with boolean value and return boolean value
