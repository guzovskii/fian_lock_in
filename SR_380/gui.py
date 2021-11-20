from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import sys
import pandas as pd


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


class MyGraphWidget(QtWidgets.QWidget):
    def __init__(self, x_list, y_list, title='---', show_x_grid=True, show_y_grid=True, color='White'):
        super().__init__()
        self.x_data = x_list[0]
        self.y_data = y_list[1]
        self.layout = QtWidgets.QGridLayout()
        self.graph_widget = pg.PlotWidget(title=title, labels={'left': y_list[1], 'bottom': x_list[0]})
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
    def __init__(self, update_graph_func, start_func, stop_func, data_names):
        self.app = QtWidgets.QApplication(sys.argv)

        self.data_list = DATA_LIST_CLASS()

        self.win = QtWidgets.QMainWindow()
        self.win.resize(1000, 1000)
        self.win.setWindowTitle('LowTempMeasurements')
        self.win.setWindowIcon(QtGui.QIcon('1x/icon.png'))
        self.win.setMinimumWidth(800)
        self.win.setMinimumHeight(900)

        self.graph_1 = MyGraphWidget(x_list=data_names, y_list=data_names)
        self.graph_2 = MyGraphWidget(x_list=data_names, y_list=data_names)
        self.graph_3 = MyGraphWidget(x_list=data_names, y_list=data_names)
        self.graph_4 = MyGraphWidget(x_list=data_names, y_list=data_names)

        self.StartButton = QtWidgets.QPushButton("START")
        self.StartButton.setIcon(QtGui.QIcon('1x/start.png'))
        self.StartButton.setIconSize(QtCore.QSize(30, 30))
        self.StartButton.setFixedWidth(150)
        self.StartButton.setFixedHeight(50)
        self.StartButton.clicked.connect(start_func)

        self.StopButton = QtWidgets.QPushButton("STOP")
        self.StopButton.setIcon(QtGui.QIcon('1x/stop.png'))
        self.StopButton.setIconSize(QtCore.QSize(30, 30))
        self.StopButton.setFixedWidth(150)
        self.StopButton.setFixedHeight(50)
        self.StopButton.clicked.connect(stop_func)

        self.FileNameInputLabel = QtWidgets.QLabel('File name:')
        self.FileNameInputLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.FileNameInputLabel.setFixedWidth(50)

        self.FileNameInput = QtWidgets.QLineEdit()
        self.FileNameInput.setAlignment(QtCore.Qt.AlignCenter)
        self.FileNameInput.returnPressed.connect(self.ConfirmFileName)

        self.ConfirmFileNameButton = QtWidgets.QPushButton("CONFIRM")
        self.ConfirmFileNameButton.setFixedWidth(100)
        self.ConfirmFileNameButton.clicked.connect(self.ConfirmFileName)
        self.ConfirmFileNameButton.setAutoDefault(True)

        self.CurrentNameLabel = QtWidgets.QLineEdit()
        self.CurrentNameLabel.setDisabled(True)
        self.CurrentNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CurrentNameLabel.setFixedWidth(250)

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
        self.update_timer.timeout.connect(update_graph_func)
        self.update_timer.setInterval(1000)

        self.win.show()

    def ConfirmFileName(self):
        self.CurrentNameLabel.setText(self.FileNameInput.text())

    def exec(self):
        self.app.exec()
