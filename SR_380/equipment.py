import pyvisa as pv
import logging
import time
from typing import Optional

def now():
    return(time.asctime(time.gmtime(time.time())))

logger = logging.getLogger(__name__)
rm = pv.ResourceManager()
print(rm.list_resources())

class SR_830():
    def __init__(self, adress: str):
        self.adress: str = adress
        self.inst = rm.open_resource(adress, )

    def name(self):
        return self.inst.query("*IDN?")

    def frequency(self, freq=None) -> Optional[float]:
        if freq == None:
            return float(self.inst.query("FREQ?").strip())
        else:
            self.inst.write(f"FREQ {freq}")
            print(self.adress, f": frequency changed to {freq} Hz")



if __name__ == "__main__":
    print("hello")