import pyvisa as pv
import pyvisa.constants
import logging
import time
from typing import Optional
import enum
import csv

mult_v = {"V": 1, "mV": 1e-3, "uV": 1e-6, "nV": 1e-9, 'pV': 1e-12}

rm = pv.ResourceManager()
print(rm.list_resources())

def now():
    return(time.asctime(time.gmtime(time.time())))

class SR_830():
    def __init__(self, address: str):
        self.address: str = address
        try:
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
        except Exception as e:
            print(e)
        # finally:
        #     print(self.address, f": FAIL to open resource")
        self.inst.clear()

    def name(self):
        try:
            print(self.inst.query("*IDN?"))
            return self.inst.query("*IDN?")
        except Exception as e:
            print(self.address, f": FAIL to get ID")
            return None

    def get_freq(self):
        try:
            return float(self.inst.query("FREQ?").strip())
        except Exception as e:
            print(self.address, f": FAIL to get frequency value")
            return None

    def set_freq(self, freq: float):
        try:
            self.inst.write(f"FREQ {freq}")
        except Exception as e:
            print(self.address, f": FAIL to set frequency")

        # if :
        #     print(self.address, f": frequency changed to {freq} Hz")
        # else:
        #     print(self.address, f": FAIL to change frequency (current freq is {cur_freq} Hz)")

    def get_data(self):
        try:
            data = [float(self.inst.query("OUTP? 1")), float(self.inst.query("OUTP? 2")),
                    float(self.inst.query("OUTP? 3")), float(self.inst.query("OUTP? 4"))]
            return data
        except Exception as e:
            print(self.address, f": FAIL to set data")
            return list([None for i in range(4)])

    def get_x(self):
        try:
            return float(self.inst.query("OUTP? 1"))
        except Exception as e:
            print(self.address, f": FAIL to get X value")
            return None

    def get_y(self):
        try:
            return float(self.inst.query("OUTP? 2"))
        except Exception as e:
            print(self.address, f": FAIL to get Y value")
            return None

    def get_ampl(self):
        try:
            return float(self.inst.query("OUTP? 3"))
        except Exception as e:
            print(self.address, f": FAIL to get amplitude value")
            return None

    def get_phase(self):
        try:
            return float(self.inst.query("OUTP? 4"))
        except Exception as e:
            print(self.address, f": FAIL to get phase value")

    def get_out_voltage(self):
        try:
            return float(self.inst.query("SLVL?"))
        except Exception as e:
            print(self.address, f": FAIL to get out_voltage value")
            return None

    def set_out_voltage(self, volt: float):
        try:
            self.inst.write(f"SLVL {volt}")
            print(self.address, f": OUT voltage changed to {volt} V")
            # cur_volt = self.get_sin_voltage()
            # if cur_volt == volt:
            #     print(self.address, f": sin voltage changed to {volt} V")
            # else:
            #     print(self.address, f": FAIL to change sin voltage (current freq is {cur_volt} V)")
        except Exception as e:
            print(self.address, f": FAIL to set out_voltage")

    def close(self):
        try:
            self.inst.close()
        except Exception as e:
            print(self.address, f": FAIL to close SR830")

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
