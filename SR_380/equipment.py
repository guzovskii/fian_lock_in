import pyvisa as pv
import pyvisa.constants
import logging
import time
from typing import Optional
import enum
import csv

mult_v = {"V": 1, "mV": 1e-3, "uV": 1e-6, "nV": 1e-9, 'pV': 1e-12}

ResourceManager = pv.ResourceManager()

InstrList = ResourceManager.list_resources()
print(InstrList)


def now():
    return time.asctime(time.gmtime(time.time()))


class SR830:
    def __init__(self, address: str):
        self.logger = logging.getLogger('log.equipment.SR830')
        self.address: str = address
        self.inst = None
        try:
            if "GPIB" in address or "gpib" in address:
                self.inst = ResourceManager.open_resource(address,)
            else:
                self.inst = ResourceManager.open_resource(
                    address,
                    baud_rate=19200,
                    parity=pv.constants.Parity.odd,
                    data_bits=8,
                    read_termination="\r"
                )
            self.inst.clear()
        except Exception as e:
            self.logger.warning(f'FAIL to initialize instrument \'{address}\' : {e}')

        self.sens_dict = {0: "2 nV / fA",
                          1: "5 nV / fA",
                          2: "10 nV / fA",
                          3: "20 nV / fA",
                          4: "50 nV / fA",
                          5: "100 nV / fA",
                          6: "200 nV / fA",
                          7: "500 nV / fA",
                          8: "1 mcV / pA",
                          9: "2 mcV / pA",
                          10: "5 mcV / pA",
                          11: "10 mcV / pA",
                          12: "20 mcV / pA",
                          13: "50 mcV / pA",
                          14: "100 mcV / pA",
                          15: "200 mcV / pA",
                          16: "500 mcV / pA",
                          17: "1 mV / nA",
                          18: "2 mV / nA",
                          19: "5 mV / nA",
                          20: "10 mV / nA",
                          21: "20 mV / nA",
                          22: "50 mV / nA",
                          23: "100 mV / nA",
                          24: "200 mV / nA",
                          25: "500 mV / nA",
                          26: "1V / fA"}

    def name(self):
        try:
            # print(self.inst.query("*IDN?"))
            return self.inst.query("*IDN?")
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get ID : {e}")
            return None

    def set_adeq_sens(self):
        while self.output_overload():
            sens = self.sens_up()
            if sens:
                break
            time.sleep(5)

    def get_freq(self):
        try:
            return float(self.inst.query("FREQ?").strip())
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get FREQUENCY value : {e}")
            return None

    def set_freq(self, freq: float):
        try:
            self.inst.write(f"FREQ {freq}")
            if self.exec_status():
                print(self.address, f": FAIL to set frequency")
            else:
                print(self.address, f": frequency changed to {freq} Hz")
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to set FREQUENCY : {e}")

    def get_data(self):
        try:
            R1.set_adeq_sens()
            data = [float(self.inst.query("OUTP? 1")), float(self.inst.query("OUTP? 2")),
                    float(self.inst.query("OUTP? 3")), float(self.inst.query("OUTP? 4"))]
            return data
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get DATA : {e}")
            return list([None for i in range(4)])

    def get_x(self):
        try:
            R1.set_adeq_sens()
            return float(self.inst.query("OUTP? 1"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get X value : {e}")
            return None

    def get_y(self):
        try:
            R1.set_adeq_sens()
            return float(self.inst.query("OUTP? 2"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get Y value : {e}")
            return None

    def get_ampl(self):
        try:
            R1.set_adeq_sens()
            return float(self.inst.query("OUTP? 3"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get AMPLITUDE value : {e}")
            return None

    def get_phase(self):
        try:
            return float(self.inst.query("OUTP? 4"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get PHASE value : {e}")

    def get_out_voltage(self):
        try:
            return float(self.inst.query("SLVL?"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get OUT VOLTAGE value : {e}")
            return None

    def set_out_voltage(self, volt: float):
        try:
            self.inst.write(f"SLVL {volt}")
            if self.exec_status():
                self.logger.warning(f"{self.address} : FAIL to set OUT VOLTAGE")
            else:
                self.logger.info(f"{self.address} : OUT VOLTAGE changed to {volt} V")
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to set OUT VOLTAGE : {e}")

    def get_sens(self):
        try:
            return int(self.inst.query("SENS?"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get SENSITIVITY value : {e}")
            return None

    def sens_up(self):
        try:
            sens = self.get_sens()
            self.set_sens(min(sens + 1, 26))
            if sens < 26:
                self.logger.info(f"{self.address} : SENSITIVITY set to {self.sens_dict[min(sens + 1, 26)]}")
                return 0
            else:
                self.logger.info(f"{self.address} : Maximum SENSITIVITY set")
                return 1
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to upgrade SENSITIVITY : {e}")
            return 0

    def sens_down(self):
        try:
            sens = self.get_sens()
            self.set_sens(max(sens - 1, 0))
            if sens > 0:
                self.logger.info(f"{self.address} : SENSITIVITY set to {self.sens_dict[min(sens - 1, 26)]}")
                return 0
            else:
                self.logger.info(f"{self.address} : Minimum SENSITIVITY set")
                return 1
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to downgrade SENSITIVITY : {e}")
            return 0

    def set_sens(self, n: int):
        try:
            self.inst.write(f"SENS {n}")
            if self.exec_status():
                self.logger.warning(f"{self.address} : FAIL to set SENSITIVITY")
            else:
                # print(self.address, f": SENSITIVITY set to {self.sens_dict[n]}")
                self.logger.info(f"{self.address} : SENSITIVITY set to {self.sens_dict[n]}")
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to set SENSITIVITY : {e}")
            return 0

    def close(self):
        try:
            self.inst.close()
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to close SR830 : {e}")

    def __del__(self):
        self.close()

    def get_ch_1(self):
        try:
            R1.set_adeq_sens()
            return float(self.inst.query("OUTR? 1"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get CH_1 value : {e}")
            return None

    def get_ch_2(self):
        try:
            R1.set_adeq_sens()
            return float(self.inst.query("OUTR? 2"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get CH_2 value : {e}")
            return None

    def get_standard_event_status(self, n: int):
        try:
            return int(self.inst.query(f"*ESR? {n}"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get STANDART EVENT STATUS BYTE {n} value : {e}")
            return None

    def get_LIA_status(self, n: int):
        try:
            return int(self.inst.query(f"LIAS? {n}"))
        except Exception as e:
            self.logger.warning(f"{self.address} : FAIL to get LIA STATUS BYTE {n} value : {e}")
            return None

    def is_query_legal(self):
        try:
            ans = self.get_standard_event_status(5)
            if ans:
                self.logger.warning(f"{self.address} : Illegal command")
            return ans
        except Exception as e:
            self.logger.warning(f'{self.address} : {e}')
            return None

    def exec_status(self):
        try:
            ans = self.get_standard_event_status(4)
            if ans:
                self.logger.warning(f"{self.address} : FAIL to execute command")
            return ans
        except Exception as e:
            self.logger.warning(f'{self.address} : {e}')
            return None

    def output_overload(self):
        try:
            ans = self.get_LIA_status(2)
            if ans:
                self.logger.warning(f"{self.address} : Output overload detected")
            return ans
        except Exception as e:
            self.logger.warning(f'{self.address} : {e}')
            return None


if __name__ == "__main__":
    print("run MAIN.PY")
    R1 = SR830("gpib0::1::instr")

    try:
        #R1.set_freq(2000000)
        err_byte = list([R1.get_standard_event_status(i) for i in range(8)])
        print(err_byte)
        err_byte = list([R1.inst.query(f'LIAS? {i}') for i in range(8)])
        print(err_byte)
        errs_byte = list([R1.inst.query(f'ERRS? {i}') for i in range(8)])
        print(errs_byte)
    finally:
        R1.close()
        ResourceManager.close()
