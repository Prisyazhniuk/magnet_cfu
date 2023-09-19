import os
import sys
import pyqtgraph as pg
import time
from random import randint

from PyQt5.QtCore import QTimer, Qt, QIODevice, pyqtSlot, pyqtSignal
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
    QComboBox
)


class CustomDoubleSpinbox(QDoubleSpinBox):
    def validate(self, text: str, pos: int) -> object:
        text = text.replace(".", ",")
        return QDoubleSpinBox.validate(self, text, pos)

    def valueFromText(self, text: str) -> float:
        text = text.replace(",", ".")
        return float(text)


class NewWindow(QMainWindow):
    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)

        layout = QVBoxLayout()
        container = QWidget()
        self.Line = QLineEdit("Some Text")
        self.lbl = QLabel('00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F')

        layout.addWidget(self.lbl)
        layout.addWidget(self.Line)
        container.setLayout(layout)

        self.setWindowTitle("Hex Code")
        self.setCentralWidget(container)
        self.resize(400, 400)

        # self.plotWidget = pg.PlotWidget(self)
        # self.plotWidget.plot([1, 2, 3, 4])
        # self.plotWidget.scene().sigMouseClicked.connect(self.onMouseClicked)
        # plt.addLegend()
        # self.c2 = plt.plot([2, 1, 4, 3], pen='b', fillLevel=0, fillBrush=(255, 255, 255, 30), name='Blue Plot')


def on_clicked_btn_open_serial_data():
    window = NewWindow()
    window.show()


class MagnetCFU(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.port = QSerialPort()
        self.graph_widget = pg.PlotWidget()
        self.timer = QTimer()
        self.timer_mang = QTimer()
        self.data_glob = ''
        self.volt_glob = ''
        self.amper_glob = ''
        self.output_te = ''
        self.buffer = bytearray()

        # Draw a graph
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


        self.x = list(range(100))  # 100 time points
        self.y = [randint(0, 100) for _ in range(100)]  # 100 data points
        pen = pg.mkPen(color=(255, 0, 0), width=15, style=Qt.DotLine)
        self.data_line = self.graph_widget.plot(self.x, self.y)
        self.graph_widget.setTitle("<span style=\"color:blue;font-size:30pt\">o.o</span>")
        styles = {'color': 'r', 'font-size': '20px'}
        self.graph_widget.setLabel('left', 'Temperature (°C)', **styles)
        self.graph_widget.setLabel('bottom', 'Hour (H)', **styles)
        self.graph_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)
        self.graph_widget.showGrid(x=True, y=True)

        # Creating interface elements
        self.hysteresis = QWidget()
        self.hysteresis.setFixedSize(500, 300)

        self.lbl_COM = QLabel("COM")
        self.lbl_I_start = QLabel("I start, A")
        self.lbl_I_stop = QLabel("I stop, A")
        self.lbl_volt = QLabel("Volt")
        self.lbl_volt.setFixedSize(45, 40)
        self.lbl_amper = QLabel("Amper")
        self.lbl_amper.setFixedSize(45, 40)
        self.lbl_step = QLabel("Step")
        self.lbl_resistance = QLabel("Resistance")
        self.lbl_loops = QLabel("Loops")
        self.lbl_interval = QLabel("Interval, ms")

        self.dsb_I_start = QDoubleSpinBox()
        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_start.setFixedSize(70, 35)
        self.dsb_I_stop = QDoubleSpinBox()
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_I_stop.setFixedSize(70, 35)
        self.dsb_step = QDoubleSpinBox()
        self.dsb_step.setRange(0.01, 0.05)
        self.dsb_step.setFixedSize(70, 35)

        self.sb_loops = QSpinBox()
        self.sb_loops.setValue(1)
        self.sb_loops.setFixedSize(45, 35)

        self.le_IDN = QLineEdit()
        self.le_IDN.setReadOnly(1)
        self.le_IDN.setFixedHeight(26)
        self.le_resistance = QLineEdit()
        self.le_resistance.setDisabled(True)
        self.le_resistance.setFixedSize(100, 35)
        self.le_volt = QLineEdit()
        self.le_volt.setDisabled(True)
        self.le_volt.setPlaceholderText("0.0")
        self.le_volt.setFixedSize(70, 35)
        self.le_amper = QLineEdit()
        self.le_amper.setDisabled(True)
        self.le_amper.setPlaceholderText("0.0")
        self.le_amper.setFixedSize(70, 35)
        self.sb_interval = QSpinBox()
        self.sb_interval.setRange(0, 10000)
        self.sb_interval.setValue(1000)
        self.sb_interval.setFixedSize(100, 35)

        self.timer_mang.setInterval(self.sb_interval.value())
        self.timer_mang.timeout.connect(self.on_btn_idn)

        self.cb_COM = QComboBox()
        self.cb_COM.setFixedWidth(90)

        self.btn_IDN = QPushButton("&IDN")
        self.btn_IDN.setFixedWidth(70)
        self.btn_set_curr = QPushButton("&Set Current")
        self.btn_set_curr.setCheckable(1)
        self.btn_stop = QPushButton("&Stop")
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCheckable(1)
        self.btn_start_meas = QPushButton("&Start Measurement")
        self.btn_start_meas.setCheckable(1)
        self.btn_open = QPushButton("&Open...")
        self.btn_save = QPushButton("&Save")

        # Config Tab
        self.btn_port_open = QPushButton("Open")
        self.btn_port_open.setCheckable(True)
        self.btn_open_serial_data = QPushButton("Open Serial data")

        self.cb_port_names = QComboBox()
        self.cb_baud_rates = QComboBox()
        self.cb_data_bits = QComboBox()
        self.cb_parity = QComboBox()
        self.cb_stop_bits = QComboBox()
        self.cb_flow_control = QComboBox()

        self.cb_port_names.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
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

        # Group Box
        self.box_1 = QGroupBox("Info")
        self.box_2 = QGroupBox("Value")
        self.box_3 = QGroupBox("Control")
        self.box_4 = QGroupBox("Hysteresis")

        # Data View parameters
        self.serial_data = QLineEdit()
        self.serial_data.setReadOnly(1)
        # self.serial_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set Alignment
        self.dsb_I_start.setAlignment(Qt.AlignCenter)
        self.dsb_I_stop.setAlignment(Qt.AlignCenter)
        self.lbl_amper.setAlignment(Qt.AlignCenter)
        self.lbl_volt.setAlignment(Qt.AlignCenter)
        self.dsb_step.setAlignment(Qt.AlignCenter)
        self.sb_loops.setAlignment(Qt.AlignCenter)
        self.le_IDN.setAlignment(Qt.AlignCenter)
        self.le_resistance.setAlignment(Qt.AlignCenter)
        self.le_volt.setAlignment(Qt.AlignCenter)
        self.le_amper.setAlignment(Qt.AlignCenter)
        self.sb_interval.setAlignment(Qt.AlignCenter)

        # Connect all serial port to comboBox "COM in Hysteresis tab"
        self.cb_COM.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        if self.cb_COM.count() == 0:
            self.cb_COM.addItem("no ports")

        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)
        # self.setFixedSize(450, 700)

        container    = QWidget()
        tabs         = QTabWidget()
        outerLayout  = QVBoxLayout()
        topLayout    = QGridLayout()
        middleLayout = QGridLayout()
        bottomLayout = QGridLayout()

        self.setStatusBar(QStatusBar(self))
        self.status_text = QLabel(self)
        self.statusBar().addWidget(self.status_text)

        tabs.addTab(self.hysteresis_tab(), "&Hysteresis")
        tabs.addTab(self.configure_tab(), "&Configure")
        topLayout.addWidget(tabs)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        outerLayout.addLayout(bottomLayout)
        container.setLayout(outerLayout)

        self.setCentralWidget(container)

    def hysteresis_tab(self):
        _hysteresis_tab = QWidget()

        outer_layout   = QVBoxLayout()
        v_outer_layout = QVBoxLayout()
        h_outer_layout = QHBoxLayout()

        hyst_layout    = QVBoxLayout()
        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()

        hyst_layout.addWidget(self.graph_widget)

        # plt.addLegend()
        # c1 = plt.plot([1, 3, 2, 4], pen='y', name='Yellow Plot')
        # c2 = plt.plot([2, 1, 4, 3], pen='b', fillLevel=0, fillBrush=(255, 255, 255, 30), name='Blue Plot')
        # c3 = plt.addLine(y=4, pen='y')

        # temp_layout = QVBoxLayout()
        # temp_layout.addWidget(widgets.plotWidget)

        top_layout.addWidget(self.lbl_COM,           0, 0, Qt.AlignCenter)
        top_layout.addWidget(self.cb_COM,            0, 1)
        top_layout.addWidget(self.btn_IDN,           1, 0)
        top_layout.addWidget(self.le_IDN,            1, 1)

        middle_layout.addWidget(self.lbl_I_start,    2, 1, Qt.AlignCenter)
        middle_layout.addWidget(self.lbl_I_stop,     0, 1, Qt.AlignCenter)
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

        middle_layout.addWidget(self.dsb_I_start,    3, 1)
        middle_layout.addWidget(self.dsb_I_stop,     1, 1)
        middle_layout.addWidget(self.dsb_step,       3, 0)
        middle_layout.addWidget(self.sb_loops,       1, 0, Qt.AlignCenter)

        bottom_layout.addWidget(self.btn_set_curr,      0, 0)
        bottom_layout.addWidget(self.btn_stop,       0, 1)
        bottom_layout.addWidget(self.btn_reset,      1, 0)
        bottom_layout.addWidget(self.btn_start_meas, 1, 1)
        bottom_layout.addWidget(self.btn_open,       2, 0)
        bottom_layout.addWidget(self.btn_save,       2, 1)

        # widgets.hysteresis.setLayout(temp_layout)
        hyst_layout.addWidget(self.hysteresis)

        # All connections
        self.btn_IDN.clicked.connect(self.on_btn_idn)
        self.btn_set_curr.clicked.connect(self.on_btn_set_curr)
        self.btn_stop.clicked.connect(self.on_btn_stop)
        self.btn_reset.clicked.connect(self.on_btn_reset)
        self.btn_start_meas.clicked.connect(self.on_btn_start_meas)
        self.btn_open.clicked.connect(self.on_btn_open)
        # self.btn_save.clicked.connect(self.on_clicked_btn_save)
        # self.port.readyRead.connect(self.read_from_port)

        self.box_1.setLayout(top_layout)
        self.box_2.setLayout(middle_layout)
        self.box_3.setLayout(bottom_layout)
        self.box_4.setLayout(hyst_layout)

        h_outer_layout.addLayout(v_outer_layout)

        v_outer_layout.addWidget(self.box_1)
        v_outer_layout.addWidget(self.box_2)
        v_outer_layout.addWidget(self.box_3)
        h_outer_layout.addWidget(self.box_4)

        outer_layout.addLayout(v_outer_layout)
        outer_layout.addLayout(h_outer_layout)

        _hysteresis_tab.setLayout(outer_layout)
        return _hysteresis_tab

    def configure_tab(self):
        _configure_tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.btn_port_open)
        layout.addWidget(self.cb_port_names)
        layout.addWidget(self.cb_baud_rates)
        layout.addWidget(self.cb_data_bits)
        layout.addWidget(self.cb_parity)
        layout.addWidget(self.cb_stop_bits)
        layout.addWidget(self.cb_flow_control)
        layout.addWidget(self.btn_open_serial_data)

        self.btn_open_serial_data.clicked.connect(on_clicked_btn_open_serial_data)

        _configure_tab.setLayout(layout)
        return _configure_tab

    # def port_write(self, flag):
    #     if flag:
    #         self.port.setBaudRate(self.cb_baud_rates())
    #         self.port.setPortName(self.cb_port_names())
    #         self.port.setDataBits(self.cb_data_bits())
    #         self.port.setParity(self.cb_parity())
    #         self.port.setStopBits(self.cb_stop_bits())
    #         self.port.setFlowControl(self.cb_flow_control())
    #         r = self.port.open(QIODevice.ReadWrite)
    #         if not r:
    #             self.status_text.setText("Port open error")
    #             self.btn_port_open.setCheckable(False)
    #             self.serial_control_enable(True)
    #         else:
    #             self.status_text.setText("Port opened")
    #             self.serial_control_enable(False)
    #     else:
    #         self.port.close()
    #         self.status_text.setText("Port closed")
    #         self.serial_control_enable(True)

    def serial_control_enable(self, flag):

        self.cb_port_names.setEnabled(flag)
        self.cb_baud_rates.setEnabled(flag)
        self.cb_data_bits.setEnabled(flag)
        self.cb_parity.setEnabled(flag)
        self.cb_stop_bits.setEnabled(flag)
        self.cb_flow_control.setEnabled(flag)

    def baud_rate(self):
        return int(self.cb_baud_rates.currentText())

    def port_name(self):
        return self.cb_port_names.currentText()

    def data_bit(self):
        return int(self.cb_data_bits.currentIndex() + 5)

    def parity(self):
        return self.cb_parity.currentIndex()

    def stop_bit(self):
        return self.cb_stop_bits.currentIndex()

    def flow_control(self):
        return self.cb_flow_control.currentIndex()

    def close_port(self):
        self.port.close()

    def receive_port(self):
        data = self.port.readAll()
        self.serial_data = data.data().decode('utf8')

        return self.serial_data

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
        # self.port.close()
        # self.status_text.setText("Port closed")
        # self.serialControlEnable(True)
        ready = self.port.open(QIODevice.ReadWrite)
        if not ready:
            self.status_text.setText("Port open error")
            self.btn_IDN.setChecked(False)
            self.serial_control_enable(True)
        else:
            self.status_text.setText("Port opened")

    # def appendSerialText(self, appendText):
    #     widgets = app_widgets.WidgetsForApp()
    #     widgets.serial_data.setText(appendText)
    #     Text = appendText.encode()

    def on_btn_idn(self):
        # self.timer_mang.start()
        self.init_port()
        self.port.write("A007*IDN?\n".encode())
        self.read_idn_from_port()

        # self.init_port()
        # self.port.write("A007MEAS:VOLT?\n".encode())
        # self.read_volt()
        #
        # self.init_port()
        # self.port.write("A007MEAS:CURR?\n".encode())
        # self.read_amper()

        
    @pyqtSlot()
    def read_idn_from_port(self):
        # good realization
        # self.serial_control_enable(False) # flag on configs serial port
        # self.port.isDataTerminalReady()
        self.port.readyRead.emit()

        while self.port.canReadLine():
            text = self.port.readLine().data().decode()
            text = text.rstrip('\r\n')
            # self.output_te = text
            # input_data = text

            self.le_IDN.setText(text)
            self.status_text.setText(text)
            self.port.close()

        # self.le_IDN.setText(self.output_te)
        # self.status_text.setText(self.output_te)

    #
    def read_volt(self):
        self.port.readyRead.emit()

        volt = self.port.readLine()
        volt_s = str(volt, 'utf-8').strip()

        self.le_volt.setText(volt_s)
        self.port.close()


    def read_amper(self):
        self.port.readyRead.emit()

        amper = self.port.readLine()
        amper_s = str(amper, 'utf-8').strip()

        self.le_amper.setText(amper_s)
        self.port.close()


    # def read_volt_amper(self):
    #
    #     while self.port.canReadLine():
    #         volt = self.port.readData(33)
    #         self.volt_glob = volt


    # def onReadSave(self):
    #     widgets = app_widgets.WidgetsForApp()
    #     rx = self.port.read(33).strip()
    #
    #     twin_le_IDN = widgets.le_IDN
    #     self.twin_le_IDN.setText(str(rx))
    #     self.status_text.setText(str(rx))
    #     print(str(rx))

        # if flag:
        #     self.port.setPortName(self.portName())
        #     self.port.setBaudRate(self.baudRate())
        #     self.port.setDataBits(self.dataBit())
        #     self.port.setParity(self.parity())
        #     self.port.setFlowControl(self.flowControl())
        #     self.port.setDataBits(self.dataBit())
        #     ready = self.port.open(QIODevice.ReadWrite)
        #     if not ready:
        #         self.status_text.setText('Send Error')
        #         widgets.btn_IDN.setChecked(False)
        #         self.serialControlEnable(True)
        #     else:
        #         self.status_text.setText('Data sent')
        #         self.serialControlEnable(False)
        # else:
        #     self.port.close()
        #     self.status_text.setText('Port closed')
        #     self.serialControlEnable(True)

    def on_btn_set_curr(self):
        pass

    def on_btn_stop(self):
        pass

    def on_btn_reset(self):
        self.le_amper.setText("test")

    def on_btn_start_meas(self):
        pass

    def on_btn_open(self):
        pass

    # def on_clicked_btn_save(self):
    #     print()

    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(randint(0, 100))  # Add a new random value.
        self.data_line.setData(self.x, self.y)  # Update the data.

    def on_mouse_clicked(self, event):
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()
        self.status_text.setText("Coordinates of the point: x = {}, y = {}".format(x, y))

    def magn_read_va(self):
        self.init_port()


