import logging
import numpy as np
import sys
import threading
import pyvisa as pv
import equipment
import time
import math
import pandas as pd
import csv # https://code.tutsplus.com/ru/tutorials/how-to-read-and-write-csv-files-in-python--cms-29907
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

WORKING_STATUS = False
NORMALIZING_STATUS = False

R1 = equipment.SR_830("gpib0::1::instr")
R1.name()

data_ampl = []
data_time = []
data_phase = []

def Start():
    global WORKING_STATUS
    if not WORKING_STATUS:
        WORKING_STATUS = True
        measurments_thread.start()
        switching_thread.start()
        print("reading started")

def Stop():
    global WORKING_STATUS
    data_ampl.clear()
    data_time.clear()
    data_phase.clear()
    WORKING_STATUS = False
    measurments_thread.join()
    if measurments_thread.is_alive():
        print("smth wrong with measurnents_thread")
    switching_thread.join()
    if switching_thread.is_alive():
        print("smth wrong with switching_thread")

    print("reading stopped")

#-------------------------GUI---------------------------
try:
    app = QtWidgets.QApplication(sys.argv)

    win = QtWidgets.QMainWindow()
    win.resize(1280, 720)

    ampl_graph = pg.PlotWidget(title="Amplitude")
    phase_graph = pg.PlotWidget(title="Phase")
    button_space = QtWidgets.QWidget()

    Stop_Button = QtWidgets.QPushButton("STOP")
    Start_Button = QtWidgets.QPushButton("START")
    Stop_Button.setFixedWidth(200)
    Start_Button.setFixedWidth(200)

    Start_Button.clicked.connect(Start)
    Stop_Button.clicked.connect(Stop)

    button_layout = QtWidgets.QHBoxLayout()
    button_layout.addWidget(Start_Button)
    button_layout.addWidget(Stop_Button)
    button_space.setLayout(button_layout)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(ampl_graph)
    layout.addWidget(phase_graph)
    layout.addWidget(button_space)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    win.setCentralWidget(widget)

    win.show()
except Exception as e:
    print(e)


ampl_graph.plot(x=data_time, y=data_ampl)
# ampl_graph.plot(x=[1, 2, 3, np.nan, 5, 6, 7, np.nan, 9, 10, 11], y=[1, 2, 3, np.nan, 3, 2, 1, np.nan, 1, 2, 3], )
phase_graph.plot(x=data_time, y=data_phase)
phase_graph.setYRange(-200, 200)
phase_graph.showGrid(x=True, y=True)
ampl_graph.showGrid(x=True, y=True)
time_pref = 0.

NAME_LINE = ["T (sec)", "R (V)", "phase (degree)", "X (V)", "Y (V)", "freq (Hz)"]

file = open("data.txt", "w", newline='')
writer = csv.DictWriter(file, delimiter="\t", fieldnames=NAME_LINE)
writer.writeheader()
freq = 0.5
lock = threading.Lock()

def read():
    global file, writer, NAME_LINE
    try:
        if WORKING_STATUS:
            global ampl_graph, phase_graph, data_ampl, time, time_pref, data_phase
            lock.acquire() #---------------------------
            if NORMALIZING_STATUS:
                new_ampl = None
                new_phase = None
                data_ampl.append(0.)
                data_phase.append(0.)
            else:
                new_ampl = R1.get_ampl()
                new_phase = R1.get_phase()
                data_ampl.append(new_ampl)
                data_phase.append(new_phase)
            new_freq = R1.get_freq()
            lock.release()  # ---------------------------
            data_time.append(time.perf_counter())

            row = [data_time[-1], new_ampl, new_phase, None, None, new_freq]
            writer.writerow(dict(zip(NAME_LINE, row)))
            if (data_time[-1] > time_pref + 1.):
                ampl_graph.plot(x=data_time, y=data_ampl, clear=True)
                phase_graph.plot(x=data_time, y=data_phase, clear=True)
                time_pref = data_time[-1]
                file.flush()
    except Exception as e:
        print(e)

def continious_measurment():
    while 1:
        if WORKING_STATUS == False:
            break
        read()
        time.sleep(0.01)

def freq_swtch():
    global freq, WORKING_STATUS, NORMALIZING_STATUS
    while freq < 100000:
        if WORKING_STATUS == False:
            break
        with lock:
            R1.set_freq(freq)
            freq *= 1.1
        NORMALIZING_STATUS = True
        time.sleep(5)
        NORMALIZING_STATUS = False
        time.sleep(3)


measurments_thread = threading.Thread(target=continious_measurment)

switching_thread = threading.Thread(target=freq_swtch)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    WORKING_STATUS = False

    measurments_thread.join()
    if measurments_thread.is_alive():
        print("smth wrong with measurments_thread")
    else:
        print('measurement_thread terminated OK')

    switching_thread.join()
    if switching_thread.is_alive():
        print("smth wrong with switching_thread")
    else:
        print('switching_thread terminated OK')

    file.close()
    R1.close()
    equipment.rm.close()