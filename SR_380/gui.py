from PyQt5 import QtGui, QtCore, QtWidgets
from SR_380.equipment import SR830, rm
import pyqtgraph as pg
import sys
import pandas as pd
import threading
import os
import numpy as np
import datetime
import csv
import logging as log
import time


class DataListClass:
    def __init__(self):
        self.names = [
            'Time',
            'T',
            'Heater_power',
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
            'W',
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


class MyGraphWidget(QtWidgets.QWidget):
    def __init__(self, x_list, y_list, title='---', show_x_grid=True, show_y_grid=True, color='White'):
        super().__init__()
        self.x_data = x_list[0]
        self.y_data = y_list[0]
        self.layout = QtWidgets.QGridLayout()
        self.graph_widget = pg.PlotWidget(title=title, labels={'left': y_list[0], 'bottom': x_list[0]})
        self.graph_widget.showGrid(x=show_x_grid, y=show_y_grid)

        self.__color_dict = dict(
            White=(255, 255, 255),
            Red=(255, 0, 0),
            Green=(0, 255, 0),
            Blue=(0, 0, 255),
            Cian=(0, 255, 255),
            Purple=(139, 0, 255),
            Pink=(255, 82, 108),
            Yellow=(255, 255, 51),
            Orange=(255, 153, 0),
        )

        self.x_cb = QtWidgets.QComboBox()
        self.x_cb.addItems(x_list)

        self.y_cb = QtWidgets.QComboBox()
        self.y_cb.addItems(y_list)

        self.__xy_item_width = 20
        self.x_item = QtWidgets.QLabel('X: ')
        self.x_item.setFixedWidth(self.__xy_item_width)
        self.x_item.setAlignment(QtCore.Qt.AlignCenter)

        self.y_item = QtWidgets.QLabel('Y: ')
        self.y_item.setFixedWidth(self.__xy_item_width)
        self.y_item.setAlignment(QtCore.Qt.AlignCenter)

        self.color_item = QtWidgets.QLabel('Color: ')
        self.color_item.setFixedWidth(40)
        self.color_item.setAlignment(QtCore.Qt.AlignCenter)

        self.pen = pg.mkPen(color=self.__color_dict[color])
        self.color_cb = QtWidgets.QComboBox()
        self.color_cb.addItems(['White', 'Red', 'Green', 'Blue', 'Cian', 'Purple', 'Pink', 'Yellow', 'Orange'])
        self.x_cb.activated.connect(self.__set_x_item)
        self.y_cb.activated.connect(self.__set_y_item)
        self.color_cb.activated.connect(self.__set_line_color)

        self.layout.addWidget(self.graph_widget, 0, 0, 1, 6)
        self.layout.addWidget(self.x_item, 1, 0)
        self.layout.addWidget(self.x_cb, 1, 1)
        self.layout.addWidget(self.y_item, 1, 2)
        self.layout.addWidget(self.y_cb, 1, 3)
        self.layout.addWidget(self.color_item, 1, 4)
        self.layout.addWidget(self.color_cb, 1, 5)
        self.setLayout(self.layout)

    def __set_x_item(self):
        self.x_data = self.x_cb.currentText()
        self.graph_widget.setLabel('bottom', self.x_cb.currentText())

    def __set_y_item(self):
        self.y_data = self.y_cb.currentText()
        self.graph_widget.setLabel('left', self.y_cb.currentText())

    def __set_line_color(self):
        self.pen = pg.mkPen(color=self.__color_dict[self.color_cb.currentText()])
        self.graph_widget.pen = pg.mkPen(color=self.__color_dict[self.color_cb.currentText()])

    def plot(self, *args, **kwargs):
        self.graph_widget.plot(pen=self.pen, *args, **kwargs)

    def setXRange(self, *args, **kwargs):
        self.graph_widget.setXRange(*args, **kwargs)

    def setYRange(self, *args, **kwargs):
        self.graph_widget.setYRange(*args, **kwargs)

    def showGrid(self, *args, **kwargs):
        self.graph_widget.showGrid(*args, **kwargs)


class MyGUI:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

        self.data_list = DataListClass()

        self.__WORKING_STATUS = False
        self.__GUI_STATUS = True
        self.__LOCK = threading.Lock()
        self.__START_DT = datetime.datetime.now()
        self.NUMBER_OF_POINTS = 10000

        self.FILE = None
        self.WRITER = None

        self.SR_inst = [None, None]
        self.K_inst = [None, None]
        self.LS_inst = [None]
        # ---------------------GUI_COMMON--------------------
        self.win = QtWidgets.QMainWindow()
        self.win.resize(1000, 1000)
        self.win.setWindowTitle('LowTempMeasurements')
        self.win.setWindowIcon(QtGui.QIcon('1x/icon.png'))
        self.win.setMinimumWidth(800)
        self.win.setMinimumHeight(900)
        # ---------------------GUI_PLOT_PAGE--------------------
        self.graph_1 = MyGraphWidget(x_list=self.data_list.names, y_list=self.data_list.names)
        self.graph_2 = MyGraphWidget(x_list=self.data_list.names, y_list=self.data_list.names)
        self.graph_3 = MyGraphWidget(x_list=self.data_list.names, y_list=self.data_list.names)
        self.graph_4 = MyGraphWidget(x_list=self.data_list.names, y_list=self.data_list.names)

        self.StartButton = QtWidgets.QPushButton("START")
        self.StartButton.setIcon(QtGui.QIcon('1x/start.png'))
        self.StartButton.setIconSize(QtCore.QSize(30, 30))
        self.StartButton.setFixedWidth(150)
        self.StartButton.setFixedHeight(50)
        self.StartButton.clicked.connect(self.__Start)

        self.StopButton = QtWidgets.QPushButton("STOP")
        self.StopButton.setIcon(QtGui.QIcon('1x/stop.png'))
        self.StopButton.setIconSize(QtCore.QSize(30, 30))
        self.StopButton.setFixedWidth(150)
        self.StopButton.setFixedHeight(50)
        self.StopButton.clicked.connect(self.__Stop)

        self.FileNameInputLabel = QtWidgets.QLabel('File name:')
        self.FileNameInputLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.FileNameInputLabel.setFixedWidth(50)

        self.FileNameInput = QtWidgets.QLineEdit()
        self.FileNameInput.setAlignment(QtCore.Qt.AlignCenter)
        self.FileNameInput.returnPressed.connect(self.__ConfirmFileName)

        self.ConfirmFileNameButton = QtWidgets.QPushButton("CONFIRM")
        self.ConfirmFileNameButton.setFixedWidth(100)
        self.ConfirmFileNameButton.clicked.connect(self.__ConfirmFileName)
        self.ConfirmFileNameButton.setAutoDefault(True)

        self.CurrentNameLabel = QtWidgets.QLineEdit()
        self.CurrentNameLabel.setDisabled(True)
        self.CurrentNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CurrentNameLabel.setFixedWidth(250)
        # ---------------------GUI_INSTRUMENTS_PAGE--------------------
        self.SRInstruments = []
        for i in range(2):
            self.SRInstruments.append(dict(
                widget=QtWidgets.QWidget(),
                layout=QtWidgets.QHBoxLayout(),
                cb=QtWidgets.QComboBox(),
                label=QtWidgets.QLabel(f' R_{i+1}: '),
                confirm_button=QtWidgets.QPushButton(),
                text_line=QtWidgets.QLineEdit(),
            ))
            

        self.file_name_layout = QtWidgets.QHBoxLayout()
        self.file_name_layout.addWidget(self.FileNameInputLabel)
        self.file_name_layout.addWidget(self.FileNameInput)
        self.file_name_layout.addWidget(self.ConfirmFileNameButton)
        self.file_name_layout.addWidget(self.CurrentNameLabel)

        self.file_name_widget = QtWidgets.QWidget()
        self.file_name_widget.setLayout(self.file_name_layout)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.StartButton)
        self.button_layout.addWidget(self.StopButton)
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_widget = QtWidgets.QWidget()
        self.button_widget.setLayout(self.button_layout)

        self.main_tab_layout = QtWidgets.QGridLayout()
        self.main_tab_layout.addWidget(self.graph_1, 0, 0)
        self.main_tab_layout.addWidget(self.graph_2, 0, 1)
        self.main_tab_layout.addWidget(self.graph_3, 1, 0)
        self.main_tab_layout.addWidget(self.graph_4, 1, 1)
        self.main_tab_layout.addWidget(self.file_name_widget, 2, 0, 1, 2)
        self.main_tab_layout.addWidget(self.button_widget, 3, 0, 1, 2)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.main_tab_layout)

        self.settings_widget = QtWidgets.QWidget()

        self.tab_widget = QtWidgets.QTabWidget()

        self.tab_widget.addTab(self.main_widget, QtGui.QIcon('1x/plots.png'), 'Plots')
        self.tab_widget.addTab(self.settings_widget, QtGui.QIcon('1x/settings.png'), 'Settings')
        self.tab_widget.setIconSize(QtCore.QSize(20, 20))
        self.win.setCentralWidget(self.tab_widget)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.__UpdateGraphs)
        self.update_timer.setInterval(1000)

        self.win.show()

        self.READING_THREAD = threading.Thread(target=self.__Reading)
        # self.PROGRAM_THREAD = threading.Thread(target=self.__Program)

    def exec(self):
        self.READING_THREAD.start()
        print('Starting GUI...')
        self.update_timer.start()
        self.app.exec()
        self.close()

    def close(self):
        print('Closing GUI...')
        if self.__WORKING_STATUS:
            self.__Stop()

        self.__GUI_STATUS = False

        for R in self.SR_inst:
            if R:
                R.close()
        for K in self.K_inst:
            if K:
                K.close()
        for LS in self.LS_inst:
            if LS:
                LS.close()

        try:
            self.READING_THREAD.join()
        except Exception as e:
            log.warning(f'Unable to join READING_THREAD\n\t{e}')
        if self.READING_THREAD.is_alive():
            log.warning("Something wrong with READING_THREAD")
        else:
            print('READING THREAD finished')
            log.info('READING_THREAD terminated OK')

        # try:
        #     self.PROGRAM_THREAD.join()
        # except Exception as e:
        #     log.warning(f'Unable to join PROGRAM_TREAD\n\t{e}')
        # if self.PROGRAM_THREAD.is_alive():
        #     log.warning("Something wrong with PROGRAM_THREAD")
        # else:
        #     log.info('PROGRAM_THREAD terminated OK')

    def __del__(self):
        self.close()

    def __ConfirmFileName(self):
        self.CurrentNameLabel.setText(self.FileNameInput.text())

    def __Start(self):
        try:
            if not self.__WORKING_STATUS:
                self.__WORKING_STATUS = True

                FileName = self.CurrentNameLabel.text().strip()
                if FileName != '':
                    isFile = os.path.isfile(FileName)
                    self.FILE = open(FileName, 'a' if isFile else 'w', newline='')
                    self.WRITER = csv.DictWriter(self.FILE, delimiter="\t", fieldnames=self.data_list.names)
                    if not isFile:
                        self.WRITER.writeheader()
                        self.WRITER.writerow(dict(zip(self.data_list.names, self.data_list.units)))

                log.info("Reading started")
                print('Reading...')
        except Exception as e:
            log.warning(f'Problem while STARTING. Check the INSTRUMENT\n\t{e}')

    def __Stop(self):
        try:
            self.__WORKING_STATUS = False
            if self.FILE:
                self.FILE.close()
            log.info("Reading stopped")
            print('Reading stopped')
        except Exception as e:
            log.warning(f'Problem while STOPPING\n\t{e}')

    def __UpdateGraphs(self):
        with self.__LOCK:
            self.graph_1.plot(x=self.data_list.data[self.graph_1.x_data],
                              y=self.data_list.data[self.graph_1.y_data],
                              clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
            self.graph_2.plot(x=self.data_list.data[self.graph_2.x_data],
                              y=self.data_list.data[self.graph_2.y_data],
                              clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
            self.graph_3.plot(x=self.data_list.data[self.graph_3.x_data],
                              y=self.data_list.data[self.graph_3.y_data],
                              clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
            self.graph_4.plot(x=self.data_list.data[self.graph_4.x_data],
                              y=self.data_list.data[self.graph_4.y_data],
                              clear=True)  # , pen=None, symbol='o', symbolBrush=None, symbolSize=1)
            if self.FILE and self.__WORKING_STATUS:
                self.FILE.flush()

    def __Reading(self):
        print('READING starting...')
        while self.__GUI_STATUS:
            time.sleep(0.2)
            if self.__WORKING_STATUS:
                dt = datetime.datetime.now() - self.__START_DT
                try:
                    new_row = dict()
                    new_row['Time'] = dt.seconds + dt.microseconds / 1e6

                    for i, LS in enumerate(self.LS_inst):
                        if LS:
                            pass
                        else:
                            new_row[f'{f"{i+1}_" if len(self.LS_inst) > 1 else ""}T'] = np.random.normal(300, 1e-2)
                            new_row[f'{f"{i+1}_" if len(self.LS_inst) > 1 else ""}Heater_Power'] = np.random.normal(1, 0.1)

                    for i, R in enumerate(self.SR_inst):
                        if R:
                            pass
                        else:
                            new_row[f'{i+1}_SR_Freq'] = None
                            new_row[f'{i+1}_SR_R'] = None
                            new_row[f'{i+1}_SR_Phase'] = None
                            new_row[f'{i+1}_SR_X'] = None
                            new_row[f'{i+1}_SR_Y'] = None

                    for i, K in enumerate(self.K_inst):
                        if K:
                            pass
                        else:
                            new_row[f'{i+1}_K_R4'] = None

                    self.data_list.data = self.data_list.data.append(new_row, ignore_index=True)
                    if len(self.data_list.data[self.data_list.names[0]]) > self.NUMBER_OF_POINTS:
                        self.data_list.data = self.data_list.data.drop(0)
                    if self.WRITER:
                        self.WRITER.writerow(new_row)

                except Exception as e:
                    log.warning(f'FAIL to read: {e}')

        log.info('READING finished')
        print('READING finished')
