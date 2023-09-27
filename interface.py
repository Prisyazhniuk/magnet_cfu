import os
import sys
import pyqtgraph as pg
import time
from random import randint
import zhinst.core
from zhinst.toolkit import Session

from PyQt5.QtCore import QTimer, Qt, QIODevice, pyqtSlot
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGridLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QWidget,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox,
    QSplitter,
    QFrame
)


class CustomDoubleSpinbox(QDoubleSpinBox):
    def validate(self, text: str, pos: int) -> object:
        text = text.replace(".", ",")
        return QDoubleSpinBox.validate(self, text, pos)

    def valueFromText(self, text: str) -> float:
        text = text.replace(",", ".")
        return float(text)


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def rev_decimal_range(start, stop, increment):
    while start > stop:
        yield start
        start -= increment


class MagnetCFU(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.port = QSerialPort()
        self.graph_widget = pg.PlotWidget()
        self.timer = QTimer()
        self.timer_mang = QTimer()
        self.output_te = ''
        self.buffer = bytearray()

        # Creating interface elements
        # Control tab
        self.cb_COM         = QComboBox()

        self.lbl_COM        = QLabel("COM")
        self.lbl_I_start    = QLabel("I start, A")
        self.lbl_I_stop     = QLabel("I stop, A")
        self.lbl_volt       = QLabel("Volt")
        self.lbl_amper      = QLabel("Amper")
        self.lbl_step       = QLabel("Step")
        self.lbl_resistance = QLabel("Resistance")
        self.lbl_loops      = QLabel("Loops")
        self.lbl_interval   = QLabel("Interval, ms")

        self.dsb_I_start    = QDoubleSpinBox()
        self.dsb_I_stop     = QDoubleSpinBox()
        self.dsb_step       = QDoubleSpinBox()

        self.sb_loops       = QSpinBox()
        self.sb_interval    = QSpinBox()

        self.le_IDN         = QLineEdit()
        self.le_resistance  = QLineEdit()
        self.le_volt        = QLineEdit()
        self.le_amper       = QLineEdit()

        self.btn_IDN        = QPushButton("&IDN")
        self.btn_set_curr   = QPushButton("&Set Current")
        self.btn_stop       = QPushButton("&Stop")
        self.btn_reset      = QPushButton("Reset")
        self.btn_start_meas = QPushButton("&Start Measurement")
        self.btn_open       = QPushButton("&Open...")
        self.btn_save       = QPushButton("&Save")

        self.box_01          = QGroupBox("Info")
        self.box_02          = QGroupBox("Value")
        self.box_03          = QGroupBox("Control")
        self.box_04          = QGroupBox("Hysteresis")

        self.lbl_volt.setFixedSize(45, 40)
        self.lbl_amper.setFixedSize(45, 40)

        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_step.setRange(0.01, 0.05)
        self.dsb_step.setFixedSize(70, 35)
        self.dsb_I_stop.setFixedSize(70, 35)
        self.dsb_I_start.setFixedSize(70, 35)
        self.dsb_I_start.setSingleStep(0.01)
        self.dsb_I_stop.setSingleStep(0.01)
        self.dsb_step.setSingleStep(0.01)

        self.sb_loops.setValue(1)
        self.sb_loops.setFixedSize(45, 35)
        self.sb_interval.setSingleStep(100)
        self.sb_interval.setRange(0, 10000)
        self.sb_interval.setValue(1000)
        self.sb_interval.setFixedSize(100, 35)

        self.le_IDN.setReadOnly(1)
        self.le_IDN.setFixedHeight(26)
        self.le_resistance.setDisabled(True)
        self.le_resistance.setFixedSize(100, 35)
        self.le_volt.setDisabled(True)
        self.le_volt.setPlaceholderText("0.00")
        self.le_volt.setFixedSize(70, 35)
        self.le_amper.setDisabled(True)
        self.le_amper.setPlaceholderText("0.00")
        self.le_amper.setFixedSize(70, 35)

        self.cb_COM.setFixedSize(90, 35)

        self.btn_IDN.setFixedWidth(70)
        self.btn_set_curr.setCheckable(True)
        self.btn_reset.setCheckable(True)
        self.btn_start_meas.setCheckable(True)

        self.dsb_I_start.setAlignment(Qt.AlignCenter)
        self.dsb_I_stop.setAlignment(Qt.AlignCenter)
        self.lbl_amper.setAlignment(Qt.AlignCenter)
        self.lbl_volt.setAlignment(Qt.AlignCenter)
        self.dsb_step.setAlignment(Qt.AlignCenter)
        self.sb_loops.setAlignment(Qt.AlignCenter)
        self.sb_interval.setAlignment(Qt.AlignCenter)
        self.le_IDN.setAlignment(Qt.AlignCenter)
        self.le_volt.setAlignment(Qt.AlignCenter)
        self.le_amper.setAlignment(Qt.AlignCenter)
        self.le_resistance.setAlignment(Qt.AlignCenter)

        # Config Tab
        self.cb_baud_rates    = QComboBox()
        self.cb_data_bits     = QComboBox()
        self.cb_parity        = QComboBox()
        self.cb_stop_bits     = QComboBox()
        self.cb_flow_control  = QComboBox()

        self.lbl_baud_rates   = QLabel("Baud Rates")
        self.lbl_data_bits    = QLabel("Data Bits")
        self.lbl_parity       = QLabel("Parity")
        self.lbl_stop_bits    = QLabel("Stop Bits")
        self.lbl_flow_control = QLabel("Flow Control")

        self.cb_baud_rates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800',
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])
        self.cb_baud_rates.setCurrentText('115200')
        self.cb_data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.cb_data_bits.setCurrentIndex(3)
        self.cb_parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])
        self.cb_parity.setCurrentIndex(0)
        self.cb_stop_bits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.cb_stop_bits.setCurrentIndex(0)
        self.cb_flow_control.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])
        self.cb_flow_control.setCurrentIndex(0)

        # Connect all serial port to comboBox "COM in Control tab"
        self.cb_COM.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        if self.cb_COM.count() == 0:
            self.cb_COM.addItem("no ports")

        # Window setting
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)

        container     = QWidget()
        tabs          = QTabWidget()
        outer_vlayout = QVBoxLayout()
        outer_hlayout = QHBoxLayout()
        hyst_outer    = QVBoxLayout()
        hyst_layout   = QVBoxLayout()
        top_layout    = QGridLayout()
        middle_layout = QGridLayout()
        bottom_layout = QGridLayout()
        bottom_sp     = QWidget()

        bottom_sp.setFixedSize(100, 130)

        hyst_layout.addWidget(self.graph_widget)

        self.box_04.setFixedSize(500, 300)
        self.box_04.setLayout(hyst_layout)

        hyst_outer.addWidget(self.box_04)
        hyst_outer.addWidget(bottom_sp)

        self.setStatusBar(QStatusBar())
        self.status_text = QLabel()
        self.statusBar().addWidget(self.status_text)

        tabs.addTab(self.control_tab(), "&Control")
        tabs.addTab(self.configure_tab(), "&Configure")
        tabs.addTab(self.lock_in_tab(), "&Lock-in")

        top_layout.addWidget(tabs)

        outer_vlayout.addLayout(top_layout)
        outer_vlayout.addLayout(middle_layout)
        outer_vlayout.addLayout(bottom_layout)
        outer_hlayout.addLayout(outer_vlayout)
        outer_hlayout.addLayout(hyst_outer)

        container.setLayout(outer_hlayout)

        self.setCentralWidget(container)

    def control_tab(self):
        _control_tab   = QWidget()

        outer_layout   = QVBoxLayout()
        v_outer_layout = QVBoxLayout()
        h_outer_layout = QHBoxLayout()

        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()

        self.box_05    = QGroupBox("COM-port")

        top_layout.addWidget(self.lbl_COM,           0, 0, Qt.AlignCenter)
        top_layout.addWidget(self.cb_COM,            0, 1)
        top_layout.addWidget(self.btn_IDN,           1, 0)
        top_layout.addWidget(self.le_IDN,            1, 1, 1, 2)

        middle_layout.addWidget(self.lbl_I_start,    0, 1, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_I_stop,     2, 1, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_volt,       2, 2, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_amper,      0, 2, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_step,       2, 0, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_loops,      0, 0, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_resistance, 0, 3, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_interval,   2, 3, Qt.AlignCenter)

        middle_layout.addWidget(self.le_amper,       1, 2)
        middle_layout.addWidget(self.le_volt,        3, 2)
        middle_layout.addWidget(self.le_resistance,  1, 3)
        middle_layout.addWidget(self.sb_interval,    3, 3)

        middle_layout.addWidget(self.dsb_I_start,    1, 1)
        middle_layout.addWidget(self.dsb_I_stop,     3, 1)
        middle_layout.addWidget(self.dsb_step,       3, 0)
        middle_layout.addWidget(self.sb_loops,       1, 0, Qt.AlignCenter)

        bottom_layout.addWidget(self.btn_set_curr,   0, 0)
        bottom_layout.addWidget(self.btn_stop,       0, 1)
        bottom_layout.addWidget(self.btn_reset,      1, 0)
        bottom_layout.addWidget(self.btn_start_meas, 1, 1)
        bottom_layout.addWidget(self.btn_open,       2, 0)
        bottom_layout.addWidget(self.btn_save,       2, 1)

        # BTN connections
        self.btn_IDN.clicked.connect(self.on_btn_idn)
        self.btn_set_curr.clicked.connect(self.on_btn_set_curr)
        self.btn_stop.clicked.connect(self.on_btn_stop)
        self.btn_reset.clicked.connect(self.on_btn_reset)
        self.btn_start_meas.clicked.connect(self.on_btn_start_meas)
        self.btn_open.clicked.connect(self.on_btn_open)

        self.box_01.setLayout(top_layout)
        self.box_02.setLayout(middle_layout)
        self.box_03.setLayout(bottom_layout)

        h_outer_layout.addLayout(v_outer_layout)

        v_outer_layout.addWidget(self.box_01)
        v_outer_layout.addWidget(self.box_02)
        v_outer_layout.addWidget(self.box_03)

        outer_layout.addLayout(v_outer_layout)
        outer_layout.addLayout(h_outer_layout)

        _control_tab.setLayout(outer_layout)
        return _control_tab

    def configure_tab(self):
        _configure_tab = QWidget()

        layout         = QVBoxLayout()
        outer_layout   = QVBoxLayout()

        layout.addWidget(self.lbl_baud_rates)
        layout.addWidget(self.cb_baud_rates)
        layout.addWidget(self.lbl_data_bits)
        layout.addWidget(self.cb_data_bits)
        layout.addWidget(self.lbl_parity)
        layout.addWidget(self.cb_parity)
        layout.addWidget(self.lbl_stop_bits)
        layout.addWidget(self.cb_stop_bits)
        layout.addWidget(self.lbl_flow_control)
        layout.addWidget(self.cb_flow_control)

        self.cb_baud_rates.setFixedSize(120, 40)
        self.cb_data_bits.setFixedSize(120, 40)
        self.cb_parity.setFixedSize(120, 40)
        self.cb_stop_bits.setFixedSize(120, 40)
        self.cb_flow_control.setFixedSize(120, 40)

        layout.setAlignment(Qt.AlignHCenter)

        self.box_05.setFixedSize(300, 600)
        self.box_05.setLayout(layout)

        outer_layout.addWidget(self.box_05)

        _configure_tab.setLayout(outer_layout)
        return _configure_tab

    def lock_in_tab(self):
        _lock_in_tab     = QWidget()

        outer_layout     = QVBoxLayout()
        v_outer_layout   = QVBoxLayout()
        h1_outer_layout  = QHBoxLayout()
        h2_outer_layout  = QHBoxLayout()

        top_layout       = QGridLayout()
        middle_layout    = QGridLayout()
        bottom_layout    = QGridLayout()

        self.le_device   = QLineEdit()
        self.le_host     = QLineEdit()
        self.le_port     = QLineEdit()
        self.le_version  = QLineEdit()

        discovery        = zhinst.core.ziDiscovery()

        discovery.find('mf-dev4999')

        dev_prop         = discovery.get('dev4999')
        serveraddress    = dev_prop['serveraddress']
        serverport       = dev_prop['serverport']
        serverversion    = dev_prop["serverversion"]

        if serveraddress == "172.16.0.35":
            self.status_text.setText("MFLI connected global")
            daq = zhinst.core.ziDAQServer(serveraddress, serverport, 6)

            # daq.setInt('/dev4999/sigins/0/autorange', 1)  # for voltage
            daq.setInt('/dev4999/demods/0/adcselect', 0)  # input signal sig in 1
            daq.setDouble('/dev4999/demods/0/timeconstant', 0.1)  # TC = 0.100
            # daq.setInt('/dev4999/demods/0/enable', 1) # data transfer streaming

            self.le_host.setText(serveraddress)
            self.le_port.setText(str(serverport))
            self.le_version.setText(str(serverversion))

            self.le_device.setText(dev_prop['devicetype'] + " " + dev_prop['deviceid'])

        elif serveraddress == "127.0.0.1":
            self.status_text.setText("MFLI connected local")
            daq = zhinst.core.ziDAQServer(serveraddress, serverport, 6)

            # daq.setInt('/dev4999/sigins/0/autorange', 1)  # for voltage
            daq.setInt('/dev4999/demods/0/adcselect', 0)  # input signal sig in 1
            daq.setDouble('/dev4999/demods/0/timeconstant', 0.1)  # TC = 0.100
            # daq.setInt('/dev4999/demods/0/enable', 1) # data transfer streaming

            self.le_host.setText(serveraddress)
            self.le_port.setText(str(serverport))
            self.le_version.setText(str(serverversion))

            self.le_device.setText(dev_prop['devicetype'] + " " + dev_prop['deviceid'])

        else:
            self.status_text.setText("MFLI not found")

        self.box_06       = QGroupBox("Lock-in")
        self.box_07       = QGroupBox("Demodulators")
        self.box_08       = QGroupBox("Signal Inputs")
        self.box_09       = QGroupBox("Signal Outputs")

        # Lock-in GroupBox
        self.lbl_wserver  = QLabel("<b>Data Server</b>")
        self.lbl_device   = QLabel("Device")
        self.lbl_host     = QLabel("host")
        self.lbl_sport    = QLabel("Port")
        self.lbl_sversion = QLabel("Version")

        self.lbl_device.setFixedHeight(35)
        self.lbl_wserver.setFixedHeight(35)
        self.lbl_sversion.setFixedHeight(35)
        self.lbl_host.adjustSize()
        self.lbl_sport.adjustSize()

        self.box_07.setFixedHeight(400)

        self.le_host.setFixedHeight(35)
        self.le_device.setFixedHeight(35)
        self.le_port.setFixedHeight(35)
        self.le_version.setFixedHeight(35)

        self.le_host.setDisabled(True)
        self.le_port.setDisabled(True)
        self.le_version.setDisabled(True)
        self.le_device.setDisabled(True)

        # Demodulators GroupBox
        self.lbl_freq     = QLabel("Freq (Hz)")
        self.lbl_sig_in   = QLabel("Sig In")
        self.lbl_phase    = QLabel("Phase (deg)")
        self.lbl_transfer = QLabel("Data Transfer")
        self.lbl_trigger  = QLabel("Trigger")
        self.lbl_tc       = QLabel("TC")
        self.lbl_order    = QLabel("Order")

        self.le_freq      = QLineEdit()
        self.le_tc        = QLineEdit()
        self.le_phase     = QLineEdit()
        self.le_transfer  = QLineEdit()

        self.btn_phase    = QPushButton("Auto")
        self.btn_transfer = QPushButton("Auto")

        self.cb_order     = QComboBox()
        self.cb_trigger   = QComboBox()

        self.le_freq.setFixedHeight(30)
        self.le_transfer.setFixedHeight(30)
        self.le_phase.setFixedHeight(30)
        self.le_tc.setFixedHeight(30)

        self.cb_order.setFixedHeight(30)
        self.cb_trigger.setFixedHeight(30)

        # Signal Inputs GroupBox
        self.lbl_range   = QLabel("Range")
        self.lbl_scaling = QLabel("Scaling")

        self.le_range    = QLineEdit()
        self.le_scaling  = QLineEdit()

        self.btn_range   = QPushButton("Auto")
        self.btn_ac      = QPushButton("AC")
        self.btn_50      = QPushButton("50 Ω")
        self.btn_float   = QPushButton("Float")

        self.btn_ac.setFixedWidth(40)
        self.btn_50.setFixedWidth(50)
        self.btn_float.setFixedWidth(50)
        self.btn_range.setFixedWidth(50)

        self.le_range.setFixedSize(50, 30)
        self.le_scaling.setFixedSize(50, 30)

        # Signal Outputs GroupBox
        self.lbl_orange     = QLabel("Range")
        self.lbl_amp        = QLabel("Amp (Vpk")

        self.le_orange      = QLineEdit()
        self.le_amp         = QLineEdit()

        self.btn_output_sig = QPushButton("On                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ")
        self.btn_auto_amp   = QPushButton("Auto")

        top_layout.addWidget(self.lbl_wserver,       0, 0, 1, 0)
        top_layout.addWidget(self.lbl_sversion,      2, 0)
        top_layout.addWidget(self.lbl_host,          1, 2)
        top_layout.addWidget(self.lbl_sport,         2, 2)
        top_layout.addWidget(self.lbl_device,        1, 0)

        top_layout.addWidget(self.le_version,        2, 1)
        top_layout.addWidget(self.le_host,           1, 3)
        top_layout.addWidget(self.le_port,           2, 3)
        top_layout.addWidget(self.le_device,         1, 1)

        top_layout.setAlignment(Qt.AlignLeft)

        middle_layout.addWidget(self.lbl_freq,       0, 0)
        middle_layout.addWidget(self.lbl_phase,      0, 1)
        middle_layout.addWidget(self.lbl_transfer,   2, 1)
        middle_layout.addWidget(self.lbl_trigger,    6, 0)
        # middle_layout.addWidget(self.lbl_sig_in,     0, 3)
        middle_layout.addWidget(self.lbl_tc,         4, 0)
        middle_layout.addWidget(self.lbl_order,      2, 0)

        middle_layout.addWidget(self.le_phase,       1, 1)
        middle_layout.addWidget(self.le_freq,        1, 0)
        middle_layout.addWidget(self.le_transfer,    3, 1)
        middle_layout.addWidget(self.le_tc,          5, 0)

        middle_layout.addWidget(self.cb_trigger,     7, 0)
        middle_layout.addWidget(self.cb_order,       3, 0)

        middle_layout.addWidget(self.btn_phase,      1, 2)
        middle_layout.addWidget(self.btn_transfer,   3, 2)

        bottom_layout.addWidget(self.lbl_range,   0, 0)
        bottom_layout.addWidget(self.le_range,    0, 1)
        bottom_layout.addWidget(self.btn_range,   0, 2)
        bottom_layout.addWidget(self.lbl_scaling, 1, 0)
        bottom_layout.addWidget(self.le_scaling,  1, 1)
        bottom_layout.addWidget(self.btn_ac,      2, 0)
        bottom_layout.addWidget(self.btn_50,      2, 2)
        bottom_layout.addWidget(self.btn_float,   2, 1)

        bottom_layout.setAlignment(Qt.AlignLeft)

        self.box_06.setLayout(top_layout)
        self.box_07.setLayout(middle_layout)
        self.box_08.setLayout(bottom_layout)

        h1_outer_layout.addWidget(self.box_06)
        h1_outer_layout.addWidget(self.box_08)

        h2_outer_layout.addWidget(self.box_07)
        h2_outer_layout.addWidget(self.box_09)

        outer_layout.addLayout(h1_outer_layout)
        outer_layout.addLayout(h2_outer_layout)

        _lock_in_tab.setLayout(outer_layout)
        return _lock_in_tab

    def serial_control_enable(self, flag):
        self.cb_COM.setEnabled(flag)
        self.cb_baud_rates.setEnabled(flag)
        self.cb_data_bits.setEnabled(flag)
        self.cb_parity.setEnabled(flag)
        self.cb_stop_bits.setEnabled(flag)
        self.cb_flow_control.setEnabled(flag)

    def baud_rate(self):
        return int(self.cb_baud_rates.currentText())

    def data_bit(self):
        return int(self.cb_data_bits.currentIndex() + 5)

    def parity(self):
        return self.cb_parity.currentIndex()

    def stop_bit(self):
        return self.cb_stop_bits.currentIndex()

    def flow_control(self):
        return self.cb_flow_control.currentIndex()

    def receive_port(self):
        self.port.waitForReadyRead(self.sb_interval.value())
        data = self.port.readAll()
        self.serial_data = data.data().decode('utf8')
        return self.serial_data.rstrip('\r\n')

    def write_port(self, data):
        self.port.writeData(data.encode())

    def write_port_list(self, data):
        for value in data:
            self.port.writeData(value.encode())

    def init_port(self):
        if not QSerialPortInfo.availablePorts():
            self.status_text.setText("no ports")
        else:
            self.port.setPortName(self.cb_COM.currentText())
            self.port.setBaudRate(int(self.cb_baud_rates.currentText()))
            self.port.setParity(self.cb_parity.currentIndex())
            self.port.setDataBits(int(self.cb_data_bits.currentIndex() + 5))
            self.port.setFlowControl(self.cb_flow_control.currentIndex())
            self.port.setStopBits(self.cb_stop_bits.currentIndex())

        ready = self.port.open(QIODevice.ReadWrite)
        if not ready:
            self.status_text.setText("Port open error")
            self.serial_control_enable(True)
        else:
            self.status_text.setText("Port opened")

    @pyqtSlot()
    def on_btn_idn(self):
        self.init_port()
        self.write_port("A007*IDN?\n")
        self.read_idn_from_port()

        self.port.write("A007MEAS:VOLT?\n".encode())
        self.read_volt()

        self.port.write("A007MEAS:CURR?\n".encode())
        self.read_amper()
        self.port.close()

    def read_idn_from_port(self):
        self.port.waitForReadyRead(self.sb_interval.value() // 2)

        while self.port.canReadLine():
            text = self.port.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.output_idn = text
            self.le_IDN.setText(text)

    def read_volt(self):
        self.port.waitForReadyRead(self.sb_interval.value())
        volt_f = 0.0

        while self.port.canReadLine():
            volt = self.port.readLine().data().decode()
            volt = volt.rstrip('\r\n')
            volt_f = float(volt)
        self.le_volt.setText("{:.2f}".format(volt_f))

    def read_amper(self):
        self.port.waitForReadyRead(self.sb_interval.value())
        amper_f = 0.0

        while self.port.canReadLine():
            amper = self.port.readLine().data().decode()
            amper = amper.rstrip('\r\n')

            amper_f = float(amper)
        self.le_amper.setText("{:.2f}".format(amper_f))

    @pyqtSlot()
    def on_btn_set_curr(self):
        self.status_text.setText("Port opened")
        self.init_port()
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007SYST:REM\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007*CLS\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007OUTP ON\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.set_curr()

    def read_polarity(self):
        self.port.waitForReadyRead(self.sb_interval.value())

        while self.port.canReadLine():
            polarity = self.port.readLine().data().decode()
            polarity = polarity.rstrip('\r\n')
            polarity = int(polarity)

            return polarity

    def set_curr(self):
        if self.dsb_I_start.value() < 0.0:
            self.port.write("*POL 2\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            for _i in decimal_range(0, abs(self.dsb_I_start.value()) + self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())
                self.btn_set_curr.setChecked(False)

        if self.dsb_I_start.value() > 0.0:
            self.port.write("*POL 1\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            for _i in decimal_range(0, self.dsb_I_start.value() + self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())
                self.btn_set_curr.setChecked(False)

    @pyqtSlot()
    def on_btn_stop(self):
        pass

    @pyqtSlot()
    def on_btn_reset(self):
        self.init_port()
        if self.dsb_I_start.value() > 0:
            for _i in rev_decimal_range(self.dsb_I_start.value() - self.dsb_step.value(),
                                        0 - self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())

            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("*POL 1\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("A007OUTP OFF\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("A007*RST\n".encode())
            self.port.close()
            self.status_text.setText("Port closed")
            self.btn_reset.setChecked(False)

        elif self.dsb_I_start.value() < 0.0:
            for _i in rev_decimal_range(abs(self.dsb_I_start.value()) - self.dsb_step.value(),
                                        0 - self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())

            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("*POL 1\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("A007OUTP OFF\n".encode())
            self.port.write("A007*RST\n".encode())
            self.port.close()
            self.status_text.setText("Port closed")
            self.btn_reset.setChecked(False)

    @pyqtSlot()
    def on_btn_start_meas(self):
        self.init_port()
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007SYST:REM\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007*CLS\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.port.write("A007OUTP ON\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        self.start_meas()

    def start_meas(self):
        if self.dsb_I_start.value() < 0.0:
            self.port.write("*POL 2\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            for _i in decimal_range(0, abs(self.dsb_I_start.value()) + self.dsb_step.value(),
                                    self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())

            for _i in rev_decimal_range(abs(self.dsb_I_start.value()) - self.dsb_step.value(),
                                        0 - self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())

            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("*POL 1\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)

            for _i in decimal_range(0, self.dsb_I_stop.value() + self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())
                self.btn_start_meas.setChecked(False)
            self.port.close()

        elif self.dsb_I_start.value() > 0.0:
            self.port.write("*POL 1\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            for _i in decimal_range(0, self.dsb_I_start.value() + self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())
                self.btn_set_curr.setChecked(False)

            for _i in rev_decimal_range(self.dsb_I_start.value() - self.dsb_step.value(),
                                        0 - self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())

            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.port.write("*POL 2\n".encode())
            self.port.waitForReadyRead(self.sb_interval.value() // 2)

            for _i in decimal_range(0, abs(self.dsb_I_stop.value()) + self.dsb_step.value(), self.dsb_step.value()):
                self.receive_port()
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                self.port.write(res.encode())
                self.btn_start_meas.setChecked(False)
            self.port.close()

    @pyqtSlot()
    def on_btn_open(self):
        pass

    @pyqtSlot()
    def on_mouse_clicked(self, event):
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()
        self.status_text.setText("Coordinates of the point: x = {}, y = {}".format(x, y))
