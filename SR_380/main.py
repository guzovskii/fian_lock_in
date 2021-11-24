import datetime
import numpy as np
import sys
import threading
import pyvisa as pv

# import SR_380.equipment as eqip
import sys
import time
import math
import pandas as pd
import csv
import pyqtgraph as pg
import logging
import os
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from SR_380.gui import MyGraphWidget, MyGUI

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)

# создаем файловый обработчик, который регистрирует отладочные сообщения
file_handler = logging.FileHandler(f'log/{datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")}.log')
# file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.DEBUG)

# создаем консольный обработчик с более высоким уровнем журнала
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# создаем форматтер и добавляем его в обработчики
format_str = '%(asctime)s - %(name)s - %(levelname)s >>> %(message)s'
format_date = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(format_str, format_date)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# добавляем настроенные обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# -------------------------GUI---------------------------

try:
    GUI = MyGUI()
except Exception as e:
    logger.warning(f"GUI error : {e}")
    raise

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        GUI.exec()
