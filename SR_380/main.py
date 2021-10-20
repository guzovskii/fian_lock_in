import logging
import numpy as np
import sys
import threading
import pyvisa as pv

# import SR_380.equipment
import equipment
import time
import math
import pandas as pd
import csv # https://code.tutsplus.com/ru/tutorials/how-to-read-and-write-csv-files-in-python--cms-29907
import pyqtgraph as pg
import logging as log
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

WORKING_STATUS = False
NORMALIZING_STATUS = False

R1 = None
# R1 = equipment.SR_830("gpib0::1::instr")
# R1.name()

data_ampl = [0.]
data_time = [0.]
data_phase = [0.]


def Start():
    global WORKING_STATUS
    try:
        if not WORKING_STATUS and R1.name() is not None:
            WORKING_STATUS = True
            measurments_thread.start()
            switching_thread.start()
            log.info("reading started")
    except Exception as e:
        log.warning(f'Start problem. Check the INSTRUMENT\n\t{e}')


def Stop():
    global WORKING_STATUS
    try:
        data_ampl.clear()
        data_time.clear()
        data_phase.clear()
        WORKING_STATUS = False
        measurments_thread.join()
        if measurments_thread.is_alive():
            log.warning("smth wrong with measurnents_thread")
        switching_thread.join()
        if switching_thread.is_alive():
            log.warning("smth wrong with switching_thread")

        log.info("reading stopped")
    except Exception as e:
        log.warning(f'Stop problem\n\t{e}')


def SelectInstr():
    global R1
    if R1:
        R1.close()
    instr = Combo_Box.currentText()
    R1 = equipment.SR_830(instr)
    R1.name()

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
    Combo_Box = QtWidgets.QComboBox()
    Combo_Box.addItems(equipment.InstrList)
    Combo_Box.activated.connect(SelectInstr)

    Stop_Button.setFixedWidth(200)
    Start_Button.setFixedWidth(200)
    Combo_Box.setFixedWidth(200)

    Start_Button.clicked.connect(Start)
    Stop_Button.clicked.connect(Stop)

    button_layout = QtWidgets.QHBoxLayout()
    button_layout.addWidget(Start_Button)
    button_layout.addWidget(Stop_Button)
    button_layout.addWidget(Combo_Box)
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
    print(f"GUI error ({e})")


ampl_graph.plot(x=data_time, y=data_ampl)#, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
# ampl_graph.plot(x=[1, 2, 3, np.nan, 5, 6, 7, np.nan, 9, 10, 11], y=[1, 2, 3, np.nan, 3, 2, 1, np.nan, 1, 2, 3], )
phase_graph.plot(x=data_time, y=data_phase)#, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
phase_graph.setYRange(-200, 200)
phase_graph.showGrid(x=True, y=True)
ampl_graph.showGrid(x=True, y=True)
time_pref = 0.

NAME_LINE = ["T (sec)", "R (V)", "phase (degree)", "X_noise (V)", "Y_noise (V)", "freq (Hz)"]

file_1 = open("phase_freq_0.01V.txt", "w", newline='')
file_2 = open("phase_freq_0.02V.txt", "w", newline='')
file_3 = open("phase_freq_0.03V.txt", "w", newline='')
writer_1 = csv.DictWriter(file_1, delimiter="\t", fieldnames=NAME_LINE)
writer_2 = csv.DictWriter(file_2, delimiter="\t", fieldnames=NAME_LINE)
writer_3 = csv.DictWriter(file_3, delimiter="\t", fieldnames=NAME_LINE)
writer_1.writeheader()
writer_2.writeheader()
writer_3.writeheader()
writer = writer_1
freq = 0.5
lock = threading.Lock()


def read():
    global writer, NAME_LINE
    try:
        if WORKING_STATUS and R1.name() is not None:
            global ampl_graph, phase_graph, data_ampl, time, time_pref, data_phase
            if not NORMALIZING_STATUS:

                with lock:
                    new_ampl = R1.get_ampl()
                    new_phase = R1.get_phase()
                    data_ampl.append(new_ampl)
                    data_phase.append(new_phase)
                    new_freq = R1.get_freq()
                    x_noise = R1.get_ch_1()
                    y_noise = R1.get_ch_2()

                row = [data_time[-1], new_ampl, new_phase, x_noise, y_noise, new_freq]
                writer.writerow(dict(zip(NAME_LINE, row)))
                data_time.append(time.perf_counter())

            if (data_time[-1] > time_pref + 1.):
                ampl_graph.plot(x=data_time, y=data_ampl)#, clear=True, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
                phase_graph.plot(x=data_time, y=data_phase)#, clear=True, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
                time_pref = data_time[-1]
                file_1.flush()
                file_2.flush()
                file_3.flush()
    except Exception as e:
        print(e)


def continious_measurment():
    while 1:
        if WORKING_STATUS == False or R1.name() is None:
            break
        read()
        time.sleep(0.01)

    log.info("MEASURER thread finished")


def switcher():
    global freq, WORKING_STATUS, NORMALIZING_STATUS, writer
    R1.set_out_voltage(0.01)
    writer = writer_1
    while freq < 100000:
        if WORKING_STATUS == False:
            return 0
        with lock:
            R1.set_freq(freq)
            freq *= 1.1
            NORMALIZING_STATUS = True
            time.sleep(5)
            NORMALIZING_STATUS = False
        time.sleep(4)

    if WORKING_STATUS == False:
        return 0
    freq = 0.5
    R1.set_out_voltage(0.02)
    writer = writer_2
    while freq < 100000:
        if WORKING_STATUS == False:
            return 0
        with lock:
            R1.set_freq(freq)
            freq *= 1.1
            NORMALIZING_STATUS = True
            time.sleep(5)
            NORMALIZING_STATUS = False
        time.sleep(3)

    if WORKING_STATUS == False:
        return 0
    freq = 0.5
    R1.set_out_voltage(0.05)
    writer = writer_3
    while freq < 100000:
        if WORKING_STATUS == False:
            return 0
        with lock:
            R1.set_freq(freq)
            freq *= 1.1
            NORMALIZING_STATUS = True
            time.sleep(5)
            NORMALIZING_STATUS = False
        time.sleep(3)

    log.info("SWITCHER thread finished")


measurments_thread = threading.Thread(target=continious_measurment)

switching_thread = threading.Thread(target=switcher)


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    WORKING_STATUS = False

    try:
        measurments_thread.join()
    except Exception as e:
        log.warning(f'Unable to join measurments_thread\n\t{e}')
    if measurments_thread.is_alive():
        log.warning("smth wrong with measurments_thread")
    else:
        log.info('measurement_thread terminated OK')

    try:
        switching_thread.join()
    except Exception as e:
        log.warning(f'Unable to join switching_thread\n\t{e}')
    if switching_thread.is_alive():
        log.warning("smth wrong with switching_thread")
    else:
        log.info('switching_thread terminated OK')

    file_1.close()
    file_2.close()
    file_3.close()
    if R1:
        try:
            R1.close()
        except Exception as e:
            log.warning(f'Unable to close INSTRUMENT\n\t{e}')
    equipment.rm.close()