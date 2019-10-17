import logging
import pyvisa as pv
import equipment
import time
import math
import pandas as pd
import csv # https://code.tutsplus.com/ru/tutorials/how-to-read-and-write-csv-files-in-python--cms-29907
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


R1 = equipment.SR_830("com3")
NAME_LINE = ["T (sec)", "R (V)", "phase (degree)", "X (V)", "Y (V)"]

file = open("data.txt", "w", newline='')
writer = csv.DictWriter(file, delimiter="\t", fieldnames=NAME_LINE)
writer.writeheader()

file.close()
x = []
t = []
phase = []

win = pg.GraphicsWindow("my test graph")
win.resize(1280, 720)

p = win.addPlot(title="x")
win.nextRow()
q = win.addPlot(title="phase")

graph_x = p.plot(x=t, y=x)
graph_phase = q.plot(x=t, y=phase)
q.setRange(yRange=(-185, 185))
q.enableAutoRange('y', False)
p.showGrid(x=True, y=True)
q.showGrid(x=True, y=True)
time_pref = 0.

def read():
    global graph_x, graph_phase, x, t, time_pref, phase
    x.append(R1.get_ampl())
    phase.append(R1.get_phase())
    t.append(time.perf_counter())
    if (t[len(t) - 1] > time_pref + 1):
        graph_x.setData(x=t, y=x)
        graph_phase.setData(x=t, y=phase)
        time_pref = t[len(t) - 1]

timer = QtCore.QTimer()
timer.timeout.connect(read)
timer.start(10)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()