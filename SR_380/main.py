import logging
import pyvisa as pv
import equipment
import time
import pandas as pd

R1 = equipment.SR_830("com3")

def write():
    time.sleep(0.5)
    print(time.perf_counter())

