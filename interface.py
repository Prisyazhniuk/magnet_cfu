import os
# import magnetControl as mc
import app_widgets as wid

from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QStatusBar,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QTabWidget,
    QCheckBox,
    QGridLayout,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox,
)


class MagnetCFU(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)


        self.ports = []
        self.serial_data = ''
        self.serial_port = QSerialPort()
        self.data_port_read = ''



        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)

        container    = QWidget()
        tabs         = QTabWidget()
        outerLayout  = QVBoxLayout()
        topLayout    = QGridLayout()
        middleLayout = QGridLayout()
        bottomLayout = QGridLayout()

        self.setStatusBar(QStatusBar(self))
        self.status_text = QLabel(self)
        self.statusBar().addWidget(self.status_text)

        tabs.addTab(self.hysteresisTabUI(), "&Hysteresis")
        tabs.addTab(self.ConfigureTabUI(), "&Configure")
        topLayout.addWidget(tabs)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        outerLayout.addLayout(bottomLayout)
        container.setLayout(outerLayout)

        baudrate = []

        self.setCentralWidget(container)
        self.resize(400, 500)

    def hysteresisTabUI(self):

        hysteresis_tab = QWidget()
        outer_layout   = QVBoxLayout()
        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()

        widgets = wid.WidgetsForApp()

        top_layout.addWidget(widgets.lbl_COM,           0, 0)
        top_layout.addWidget(widgets.cb_COM,            0, 1)
        top_layout.addWidget(widgets.btn_IDN,           1, 0)
        top_layout.addWidget(widgets.lbl_Resistance,    2, 0)
        top_layout.addWidget(widgets.le_IDN,            1, 1)
        top_layout.addWidget(widgets.le_Resistance,     2, 1)

        middle_layout.addWidget(widgets.lbl_I_start,    0, 0)
        middle_layout.addWidget(widgets.lbl_I_stop,     2, 0)
        middle_layout.addWidget(widgets.lbl_Volt,       2, 2)
        middle_layout.addWidget(widgets.lbl_Amper,      0, 2)
        middle_layout.addWidget(widgets.lbl_Step,       0, 1)
        middle_layout.addWidget(widgets.lbl_Loops,      2, 1)

        middle_layout.addWidget(widgets.dsb_I_start,    1, 0)
        middle_layout.addWidget(widgets.dsb_I_stop,     3, 0)
        middle_layout.addWidget(widgets.dsb_Step,       1, 1)
        middle_layout.addWidget(widgets.sb_Loops,       3, 1)
        middle_layout.addWidget(widgets.le_Amper,       1, 2)
        middle_layout.addWidget(widgets.le_Volt,        3, 2)

        bottom_layout.addWidget(widgets.btn_Start,      0, 0)
        bottom_layout.addWidget(widgets.btn_Stop,       0, 1)
        bottom_layout.addWidget(widgets.btn_Reset,      1, 0)
        bottom_layout.addWidget(widgets.btn_Start_Meas, 1, 1)
        bottom_layout.addWidget(widgets.btn_Open,       2, 0)
        bottom_layout.addWidget(widgets.btn_Save,       2, 1)

        box_1 = QGroupBox("Info")
        box_2 = QGroupBox("Value")
        box_3 = QGroupBox("Control")
        # box_1.setFont(QFont("Verdana", 10))

        box_1.setLayout(top_layout)
        box_2.setLayout(middle_layout)
        box_3.setLayout(bottom_layout)

        outer_layout.addWidget(box_1)
        outer_layout.addWidget(box_2)
        outer_layout.addWidget(box_3)

        hysteresis_tab.setLayout(outer_layout)
        return hysteresis_tab

    def ConfigureTabUI(self):
        configure_tab = QWidget()
        layout = QVBoxLayout()

        btn_port_open = QPushButton("Open")
        btn_port_open.setCheckable(True)

        cb_port_names = QComboBox()
        cb_port_names.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        # for port in QSerialPortInfo().availablePorts():
        #     cb_port_names.addItems([str(port)])

        cb_baud_rates = QComboBox()
        cb_baud_rates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800',
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])

        cb_data_bits = QComboBox()
        cb_data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])

        _parity = QComboBox()
        _parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])

        cb_stop_bits = QComboBox()
        cb_stop_bits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])

        _flowControl = QComboBox()
        _flowControl.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])

        layout.addWidget(btn_port_open)
        layout.addWidget(cb_port_names)
        layout.addWidget(cb_baud_rates)
        layout.addWidget(cb_data_bits)
        layout.addWidget(_parity)
        layout.addWidget(cb_stop_bits)
        layout.addWidget(_flowControl)
        configure_tab.setLayout(layout)

        return configure_tab


    def close_port(self):
        self.serial_port.close()

    def receive_port(self):
        data = self.serial_port.readAll()
        self.serialData = data.data().decode('utf8')

        return self.serialData

    def receive_data(self):
        dataRead = self.serial_port.read(1).decode('utf8')

        self.packet_received.emit(dataRead)

    def receive_multiple_data(self):
        data = self.serial_port.readAll()

        dataRead = data.data().decode('utf8')

        self.packet_received.emit(dataRead)

    def write_port(self, data):
        self.serial_port.writeData(data.encode())

    def write_port_list(self, data):
        for value in data:
            self.serial_port.writeData(value.encode())


    def init_port(self):

        portOpen = self.serialPort.open()

        if portOpen:
            self.serial_port.setBaudRate(QSerialPort.Baud115200)
            self.serial_port.setDataBits(QSerialPort.Data8)
            self.serial_port.setParity(QSerialPort.NoParity)
            self.serial_port.setStopBits(QSerialPort.OneStop)
            self.serial_port.setFlowControl(QSerialPort.NoFlowControl)

            return True

        else:
            return False
