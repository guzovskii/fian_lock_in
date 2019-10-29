import pyvisa as pv
import pyvisa.constants
import logging
import time
from typing import Optional
import enum
import csv

class OUTP(enum.Enum):
    X = '1'
    Y = '2'
    Ampl = '3'
    Phase = '4'

mult_v = {"mV": 1e-3, "V": 1, "uV": 1e-6, "nV": 1e-9}

def now():
    return(time.asctime(time.gmtime(time.time())))

logger = logging.getLogger(__name__)
rm = pv.ResourceManager()
print(rm.list_resources())

class SR_830():
    def __init__(self, address: str):
        self.address: str = address
        if "GPIB" in address or "gpib" in address:
            self.inst = rm.open_resource(address,)
        else:
            self.inst = rm.open_resource(
                address,
                baud_rate=19200,
                parity=pv.constants.Parity.odd,
                data_bits=8,
                read_termination="\r"
            )
        self.inst.clear()

    def name(self):
        print(self.inst.query("*IDN?"))
        return self.inst.query("*IDN?")

    def get_freq(self):
        return float(self.inst.query("FREQ?").strip())

    def set_freq(self, freq: float):
        self.inst.write(f"FREQ {freq}")

        # if :
        #     print(self.address, f": frequency changed to {freq} Hz")
        # else:
        #     print(self.address, f": FAIL to change frequency (current freq is {cur_freq} Hz)")

    def get_data(self):
        data = [float(self.inst.query("OUTP? 1")), float(self.inst.query("OUTP? 2")),
                float(self.inst.query("OUTP? 3")), float(self.inst.query("OUTP? 4"))]
        return data

    def get_x(self):
        return float(self.inst.query("OUTP? 1"))

    def get_y(self):
        return float(self.inst.query("OUTP? 2"))

    def get_ampl(self):
        return float(self.inst.query("OUTP? 3"))

    def get_phase(self):
        return float(self.inst.query("OUTP? 4"))

    def get_sin_voltage(self):
        return float(self.inst.query("SLVL?"))

    def set_sin_voltage(self, volt: float):
        self.inst.write(f"SLVL {volt}")
        cur_volt = self.get_sin_voltage()
        if cur_volt == volt:
            print(self.address, f": sin voltage changed to {volt} V")
        else:
            print(self.address, f": FAIL to change sin voltage (current freq is {cur_volt} V)")

    def close(self):
        self.inst.close()

if __name__ == "__main__":
    print("run MAIN.PY")
    R1 = SR_830("gpib0::1::instr")

    try:
        R1.set_freq(2000000)
        err_byte = list([R1.inst.query(f'LIAS? {i}') for i in range(8)])
        print(err_byte)
        errs_byte = list([R1.inst.query(f'ERRS? {i}') for i in range(8)])
        print(errs_byte)
    finally:
        R1.close()
        rm.close()
