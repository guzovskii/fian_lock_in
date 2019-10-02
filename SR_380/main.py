import logging
import pyvisa as pv
import equipment
import datetime

time = datetime.datetime.now()

print(type(datetime.datetime.now()))

#inst = equipment.SR_830('ASRL3::INSTR')
#print(inst.name())

#rm = pv.ResourceManager()
#print(rm.list_resources())
#inst = rm.open_resource('GPIB0::1::INSTR')
#print(inst.query("*IDN?"))