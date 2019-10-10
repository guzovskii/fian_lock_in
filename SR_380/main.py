import logging
import pyvisa as pv
import equipment
import time
import pandas as pd
import csv # https://code.tutsplus.com/ru/tutorials/how-to-read-and-write-csv-files-in-python--cms-29907

R1 = equipment.SR_830("com3")
NAME_LINE = ["T (sec)", "R (V)", "phase (degree)", "X (V)", "Y (V)"]

file = open("data.txt", "w", newline='')
writer = csv.DictWriter(file, delimiter="\t", fieldnames=NAME_LINE)
writer.writeheader()

while 1:
#    print("ok")
    line = [time.perf_counter(), R1.get_ampl(), R1.get_phase(), R1.get_x(), R1.get_y()]
    writer.writerow(dict(zip(NAME_LINE, line)))
#    file.flush()
    print(line)

file.close()

