import sys
import threading
import time
import equipment
import pyqtgraph as pg
import logging as log
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

WORKING_STATUS = False
R1 = None
log.basicConfig(level=log.INFO)
GUI_ON = None
LOCK = threading.Lock()


def user_program_test():
    while GUI_ON:
        while not WORKING_STATUS:
            pass
        while 1:
            if not WORKING_STATUS:
                log.info("USER thread is waiting")
                break
            try:
                time.sleep(1)
            except Exception as e:
                log.warning(f'\t{threading.current_thread().name}:\tException\n\t{e}')
                break


def continuous_measurement():
    while GUI_ON:
        while not WORKING_STATUS:
            pass
        while 1:
            if not WORKING_STATUS:
                log.info("USER thread is waiting")
                break
            try:
                print('1')
                time.sleep(1)
            except Exception as e:
                log.warning(f'\t{threading.current_thread().name}:\tException\n\t{e}')
                break


class Gui:
    def __init__(self, user_program):
        global GUI_ON
        GUI_ON = True
        self.user_program_thread = threading.Thread(target=user_program)
        self.measurement_thread = threading.Thread(target=continuous_measurement)

    def StartGUI(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def close(self):
        self.__del__()

    def __del__(self):
        global WORKING_STATUS, GUI_ON
        StopButton()
        GUI_ON = False

        try:
            log.info('Trying to join measurement_thread...')
            self.measurement_thread.join()
        except Exception as e:
            log.warning(f'Unable to join measurement_thread\n\t{e}')
        if self.measurement_thread.is_alive():
            log.warning("smth wrong with measurement_thread")
        else:
            log.info('measurement_thread terminated OK')

        try:
            log.info('Trying to join user_program_thread...')
            self.user_program_thread.join()
        except Exception as e:
            log.warning(f'Unable to join switching_thread\n\t{e}')
        if self.user_program_thread.is_alive():
            log.warning("smth wrong with user_program_thread")
        else:
            log.info('switching_thread terminated OK')


gui = Gui(user_program_test)


def SelectInstr():
    global R1
    if R1:
        R1.close()
    instr = Combo_Box.currentText()
    R1 = equipment.SR_830(instr)
    R1.name()


def StartButton():
    global WORKING_STATUS
    try:
        if not WORKING_STATUS:
            WORKING_STATUS = True
            if not gui.measurement_thread.is_alive():
                gui.measurement_thread.start()
            if not gui.user_program_thread.is_alive():
                gui.user_program_thread.start()
            log.info("Program started")
        else:
            log.info("Program already STARTED")
    except Exception as e:
        log.warning(f'StartProcess problem. Check the INSTRUMENT\n\t{e}')


def StopButton():
    global WORKING_STATUS
    try:
        # data_ampl.clear()
        # data_time.clear()
        # data_phase.clear()
        WORKING_STATUS = False
        # gui.measurement_thread.join()
        # if gui.measurement_thread.is_alive():
        #     log.warning("smth wrong with measurements_thread")
        # gui.user_program_thread.join()
        # if gui.user_program_thread.is_alive():
        #     log.warning("smth wrong with user_program_thread")

        log.info("Program stopped")
    except Exception as e:
        log.warning(f'StopProcess problem\n\t{e}')


# -------------------------GUI---------------------------
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

    Start_Button.clicked.connect(StartButton)
    Stop_Button.clicked.connect(StopButton)

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
    log.warning(f"GUI error\n\t{e}")

if __name__ == '__main__':
    gui.StartGUI()
    gui.close()

    # if R1:
    #     try:
    #         R1.close()
    #     except Exception as e:
    #         log.warning(f'Unable to close INSTRUMENT\n\t{e}')
    # equipment.rm.close()