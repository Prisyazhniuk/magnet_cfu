import os
import app_widgets
# import magnetControl as mc

from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QLabel,
    QWidget,
    QTabWidget,
    QGridLayout
)


class MagnetCFU(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)


        self.ports = []
        self.serial_data = ''
        self.port = QSerialPort()
        self.data_port_read = ''



        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)
        self.setFixedSize(450, 700)

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
        # self.resize(400, 500)


    def hysteresisTabUI(self):
        hysteresis_tab = QWidget()

        outer_layout   = QVBoxLayout()
        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()

        widgets = app_widgets.WidgetsForApp()

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


        widgets.box_1.setLayout(top_layout)
        widgets.box_2.setLayout(middle_layout)
        widgets.box_3.setLayout(bottom_layout)

        outer_layout.addWidget(widgets.box_1)
        outer_layout.addWidget(widgets.box_2)
        outer_layout.addWidget(widgets.box_3)

        hysteresis_tab.setLayout(outer_layout)
        return hysteresis_tab

    def ConfigureTabUI(self):
        configure_tab = QWidget()
        widgets = app_widgets.WidgetsForApp()
        layout = QVBoxLayout()

        layout.addWidget(widgets.btn_port_open)
        layout.addWidget(widgets.cb_port_names)
        layout.addWidget(widgets.cb_baud_rates)
        layout.addWidget(widgets.cb_data_bits)
        layout.addWidget(widgets.cb_parity)
        layout.addWidget(widgets.cb_stop_bits)
        layout.addWidget(widgets.cb_flowControl)
        configure_tab.setLayout(layout)

        return configure_tab

    def portOpen(self, flag):
        widgets = app_widgets.WidgetsForApp()
        if flag:
            self.port.setBaudRate(widgets.cb_baud_rates())
            self.port.setPortName(widgets.cb_port_names())
            self.port.setDataBits(widgets.cb_data_bits())
            self.port.setParity(widgets.cb_parity())
            self.port.setStopBits(widgets.cb_stop_bits())
            self.port.setFlowControl(widgets.cb_flowControl())
            r = self.port.open(QIODevice.ReadWrite)
            if not r:
                self.status_text.setText("Port open error")
                widgets.btn_port_open.setCheckable(False)
                self.serialControlEnable(True)
            else:
                self.status_text.setText("Port opened")
                self.serialControlEnable(False)
        else:
            self.port.close()
            self.status_text.setText("Port closed")
            self.serialControlEnable(True)

    # def SerialDataView(self):


    def serialControlEnable(self, flag):
        widgets = app_widgets.WidgetsForApp()
        widgets.cb_port_names.setEnabled(flag)
        widgets.cb_baud_rates.setEnabled(flag)
        widgets.cb_data_bits.setEnabled(flag)
        widgets.cb_parity.setEnabled(flag)
        widgets.cb_stop_bits.setEnabled(flag)
        widgets.cb_flowControl.setEnabled(flag)

    def baudRate(self):
        widgets = app_widgets.WidgetsForApp()
        return int(widgets.cb_baud_rates.currentText())

    def portName(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_port_names.currentText()

    def dataBit(self):
        widgets = app_widgets.WidgetsForApp()
        return int(widgets.cb_data_bits.currentText() + 5)

    def parity(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_parity.currentIndex()

    def stopBit(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_stop_bits.currentIndex()

    def flowControl(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_flowControl.currentIndex()


    # def close_port(self):
    #     self.serial_port.close()
    #
    # def receive_port(self):
    #     data = self.serial_port.readAll()
    #     self.serialData = data.data().decode('utf8')
    #
    #     return self.serialData
    #
    # def receive_data(self):
    #     dataRead = self.serial_port.read(1).decode('utf8')
    #
    #     self.packet_received.emit(dataRead)
    #
    # def receive_multiple_data(self):
    #     data = self.serial_port.readAll()
    #
    #     dataRead = data.data().decode('utf8')
    #
    #     self.packet_received.emit(dataRead)
    #
    # def write_port(self, data):
    #     self.serial_port.writeData(data.encode())
    #
    # def write_port_list(self, data):
    #     for value in data:
    #         self.serial_port.writeData(value.encode())
    #
    #
    # def init_port(self):
    #
    #     portOpen = self.serialPort.open()
    #
    #     if portOpen:
    #         self.serial_port.setBaudRate(QSerialPort.Baud115200)
    #         self.serial_port.setDataBits(QSerialPort.Data8)
    #         self.serial_port.setParity(QSerialPort.NoParity)
    #         self.serial_port.setStopBits(QSerialPort.OneStop)
    #         self.serial_port.setFlowControl(QSerialPort.NoFlowControl)
    #
    #         return True
    #
    #     else:
    #         return False
