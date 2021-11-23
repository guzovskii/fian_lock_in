import datetime
import numpy as np
import sys
import threading
import pyvisa as pv

# import SR_380.equipment as eqip
import equipment
import time
import math
import pandas as pd
import csv
import pyqtgraph as pg
import logging
import os
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from SR_380.gui import MyGraphWidget, MyGUI

WORKING_STATUS = False
GUI_STATUS = True
LOCK = threading.Lock()
START_DT = datetime.datetime.now()
NUMBER_OF_POINTS = 10000

R1 = None
R2 = None
K1 = None
K2 = None

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)

# создаем файловый обработчик, который
# регистрирует отладочные сообщения
# fh = logging.FileHandler(datetime.datetime.now().strftime("log_%m-%d-%Y_%H_%M_%S") + '.log')
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)

# создаем консольный обработчик
# с более высоким уровнем журнала
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# создаем форматтер и добавляем его в обработчики
fmtstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
fmtdate = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmtstr, fmtdate)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# добавляем настроенные обработчики в логгер
logger.addHandler(fh)
logger.addHandler(ch)

# logging.info('logger')


class DATA_LIST_CLASS:
    def __init__(self):
        self.names = [
            'Time',
            'T',
            '1_SR_Freq',
            '1_SR_R',
            '1_SR_Phase',
            '1_SR_X',
            '1_SR_Y',
            '2_SR_Freq',
            '2_SR_R',
            '2_SR_Phase',
            '2_SR_X',
            '2_SR_Y',
            '1_K_R4',
            '2_K_R4',
        ]
        self.units = [
            'sec',
            'K',
            'Hz',
            'V',
            'deg',
            'V',
            'V',
            'Hz',
            'V',
            'deg',
            'V',
            'V',
            'Ohm',
            'Ohm',
        ]
        self.data = pd.DataFrame({key: np.array([]) for key in self.names})


DATA_LIST = DATA_LIST_CLASS()

FILE = None
WRITER = None


def WriteRow(row):
    if len(row) != len(DATA_LIST.names):
        log.warning('WriteRow Error: Incorrect number of values')
    else:
        if WRITER:
            WRITER.writerow(dict(zip(DATA_LIST.names, row)))


WriteRow(DATA_LIST.units)


def Start():
    global WORKING_STATUS, FILE, WRITER
    try:
        if not WORKING_STATUS:
            WORKING_STATUS = True

            FileName = CurrentNameLabel.text().strip()
            if FileName != '':
                isFile = os.path.isfile(FileName)
                FILE = open(FileName, 'a' if isFile else 'w', newline='')
                WRITER = csv.DictWriter(FILE, delimiter="\t", fieldnames=DATA_LIST.names)
                if not isFile:
                    WRITER.writeheader()
                    WriteRow(DATA_LIST.units)

            log.info("Reading started")
    except Exception as e:
        log.warning(f'Problem while STARTING. Check the INSTRUMENT\n\t{e}')


def Stop():
    global WORKING_STATUS
    try:
        WORKING_STATUS = False
        if FILE:
            FILE.close()
        log.info("Reading stopped")
    except Exception as e:
        log.warning(f'Problem while STOPPING\n\t{e}')


def ConfirmFileName():
    CurrentNameLabel.setText(FileNameInput.text())


def SelectInstr():
    global R1
    if R1_CB.currentText() == 'None':
        pass
    else:
        try:
            R1 = equipment.SR_830(R1_CB.currentText())
            if R1.name() is None:
                R1_CB.setCurrentIndex(0)
            else:
                log.info(f'Instrument {R1.name()} connected')
        except Exception as e:
            log.warning(f'FAIL to connect instrument {R1_CB.currentText()}: {e}')


def UpdateGraphs():
    with LOCK:
        graph_1.plot(x=DATA_LIST.data[graph_1.x_data],
                     y=DATA_LIST.data[graph_1.y_data],
                     clear=True)  #, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
        graph_2.plot(x=DATA_LIST.data[graph_2.x_data],
                     y=DATA_LIST.data[graph_2.y_data],
                     clear=True)  #, pen=None, symbol='o', symbolBrush=None, symbolSize=1)
        graph_3.plot(x=DATA_LIST.data[graph_3.x_data],
                     y=DATA_LIST.data[graph_3.y_data],
                     clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
        graph_4.plot(x=DATA_LIST.data[graph_4.x_data],
                     y=DATA_LIST.data[graph_4.y_data],
                     clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
        if FILE and WORKING_STATUS:
            FILE.flush()


def Reading():
    global DATA_LIST
    while GUI_STATUS:
        time.sleep(0.2)
        if WORKING_STATUS:
            dt = datetime.datetime.now() - START_DT
            try:
                new_row = dict()
                new_row['Time'] = dt.seconds + dt.microseconds / 1e6
                new_row['T'] = np.random.normal(15)
                if R1:
                    pass
                else:
                    new_row['1_SR_Freq'] = None
                    new_row['1_SR_R'] = None
                    new_row['1_SR_Phase'] = None
                    new_row['1_SR_X'] = None
                    new_row['1_SR_Y'] = None

                if R2:
                    pass
                else:
                    new_row['2_SR_Freq'] = None
                    new_row['2_SR_R'] = None
                    new_row['2_SR_Phase'] = None
                    new_row['2_SR_X'] = None
                    new_row['2_SR_Y'] = None

                if K1:
                    pass
                else:
                    new_row['1_K_R4'] = None

                if K2:
                    pass
                else:
                    new_row['2_K_R4'] = None

                DATA_LIST.data = DATA_LIST.data.append(new_row, ignore_index=True)
                if len(DATA_LIST.data[DATA_LIST.names[0]]) > NUMBER_OF_POINTS:
                    DATA_LIST.data = DATA_LIST.data.drop(0)
                if WRITER:
                    WRITER.writerow(new_row)

            except Exception as e:
                log.warning(f'FAIL to read: {e}')

    log.info('READING finished')


def Program():
    while GUI_STATUS:
        time.sleep(1)

    log.info('PROGRAM finished')


# READING_THREAD = threading.Thread(target=Reading)
# PROGRAM_THREAD = threading.Thread(target=Program)


# -------------------------GUI---------------------------


try:
    GUI = MyGUI()

    # app = QtWidgets.QApplication(sys.argv)
    #
    # win = QtWidgets.QMainWindow()
    # win.resize(1000, 1000)
    # win.setWindowTitle('LowTempMeasurements')
    # win.setWindowIcon(QtGui.QIcon('1x/icon.png'))
    # win.setMinimumWidth(800)
    # win.setMinimumHeight(900)
    #
    # graph_1 = MyGraphWidget(x_list=DATA_LIST.names, y_list=DATA_LIST.names)
    # graph_2 = MyGraphWidget(x_list=DATA_LIST.names, y_list=DATA_LIST.names)
    # graph_3 = MyGraphWidget(x_list=DATA_LIST.names, y_list=DATA_LIST.names)
    # graph_4 = MyGraphWidget(x_list=DATA_LIST.names, y_list=DATA_LIST.names)
    #
    # StartButton = QtWidgets.QPushButton("START")
    # StartButton.setIcon(QtGui.QIcon('1x/start.png'))
    # StartButton.setIconSize(QtCore.QSize(30, 30))
    # StartButton.setFixedWidth(150)
    # StartButton.setFixedHeight(50)
    # StartButton.clicked.connect(Start)
    #
    # StopButton = QtWidgets.QPushButton("STOP")
    # StopButton.setIcon(QtGui.QIcon('1x/stop.png'))
    # StopButton.setIconSize(QtCore.QSize(30, 30))
    # StopButton.setFixedWidth(150)
    # StopButton.setFixedHeight(50)
    # StopButton.clicked.connect(Stop)
    #
    # FileNameInputLabel = QtWidgets.QLabel('File name:')
    # FileNameInputLabel.setAlignment(QtCore.Qt.AlignCenter)
    # FileNameInputLabel.setFixedWidth(50)
    #
    # FileNameInput = QtWidgets.QLineEdit()
    # FileNameInput.setAlignment(QtCore.Qt.AlignCenter)
    # FileNameInput.returnPressed.connect(ConfirmFileName)
    #
    # ConfirmFileNameButton = QtWidgets.QPushButton("CONFIRM")
    # ConfirmFileNameButton.setFixedWidth(100)
    # ConfirmFileNameButton.clicked.connect(ConfirmFileName)
    # ConfirmFileNameButton.setAutoDefault(True)
    #
    # CurrentNameLabel = QtWidgets.QLineEdit()
    # CurrentNameLabel.setDisabled(True)
    # CurrentNameLabel.setAlignment(QtCore.Qt.AlignCenter)
    # CurrentNameLabel.setFixedWidth(250)
    #
    # file_name_layout = QtWidgets.QHBoxLayout()
    # file_name_layout.addWidget(FileNameInputLabel)
    # file_name_layout.addWidget(FileNameInput)
    # file_name_layout.addWidget(ConfirmFileNameButton)
    # file_name_layout.addWidget(CurrentNameLabel)
    #
    # file_name_widget = QtWidgets.QWidget()
    # file_name_widget.setLayout(file_name_layout)
    #
    # button_layout = QtWidgets.QHBoxLayout()
    # button_layout.addWidget(StartButton)
    # button_layout.addWidget(StopButton)
    # button_layout.setAlignment(QtCore.Qt.AlignCenter)
    #
    # button_widget = QtWidgets.QWidget()
    # button_widget.setLayout(button_layout)
    #
    # main_tab_layout = QtWidgets.QGridLayout()
    # main_tab_layout.addWidget(graph_1, 0, 0)
    # main_tab_layout.addWidget(graph_2, 0, 1)
    # main_tab_layout.addWidget(graph_3, 1, 0)
    # main_tab_layout.addWidget(graph_4, 1, 1)
    # main_tab_layout.addWidget(file_name_widget, 2, 0, 1, 2)
    # main_tab_layout.addWidget(button_widget, 3, 0, 1, 2)
    #
    # main_widget = QtWidgets.QWidget()
    # main_widget.setLayout(main_tab_layout)
    #
    # settings_widget = QtWidgets.QWidget()
    #
    # tab_widget = QtWidgets.QTabWidget()
    #
    # tab_widget.addTab(main_widget, QtGui.QIcon('1x/plots.png'), 'Plots')
    # tab_widget.addTab(settings_widget, QtGui.QIcon('1x/settings.png'), 'Settings')
    # tab_widget.setIconSize(QtCore.QSize(20, 20))
    # win.setCentralWidget(tab_widget)
    #
    # update_timer = QtCore.QTimer()
    # update_timer.timeout.connect(UpdateGraphs)
    # update_timer.setInterval(1000)
    #
    # win.show()
except Exception as e:
    print(f"GUI error ({e})")
    raise

if __name__ == '__main__':
    import sys

    # READING_THREAD.start()
    # PROGRAM_THREAD.start()

    # update_timer.start()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # app.exec_()
        GUI.exec()

    # GUI.close()
    # GUI_STATUS = False

    # try:
    #     READING_THREAD.join()
    # except Exception as e:
    #     log.warning(f'Unable to join READING_THREAD\n\t{e}')
    # if READING_THREAD.is_alive():
    #     log.warning("Something wrong with READING_THREAD")
    # else:
    #     log.info('READING_THREAD terminated OK')
    #
    # try:
    #     PROGRAM_THREAD.join()
    # except Exception as e:
    #     log.warning(f'Unable to join PROGRAM_TREAD\n\t{e}')
    # if PROGRAM_THREAD.is_alive():
    #     log.warning("Something wrong with PROGRAM_THREAD")
    # else:
    #     log.info('PROGRAM_THREAD terminated OK')

    equipment.rm.close()
