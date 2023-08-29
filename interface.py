import os
import sys
import app_widgets
import pyqtgraph as pg
from random import randint

from PyQt5.QtCore import QTimer, Qt, pyqtSlot, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QWidget,
    QTabWidget,
    QGridLayout
)


class MagnetCFU(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        widgets = app_widgets.WidgetsForApp()
        self.port = QSerialPort()

        self.graph_widget = pg.PlotWidget()
        self.timer = QTimer()
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
        self.graph_widget.scene().sigMouseClicked.connect(self.onMouseClicked)
        self.graph_widget.showGrid(x=True, y=True)

        # self.ports = []
        # self.serial_data = ''
        # self.data_port_read = ''
        self.twin_le_IDN = widgets.le_IDN
        self.twin_btn_IDN = widgets.btn_IDN

        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)
        #self.setFixedSize(450, 700)

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

        self.setCentralWidget(container)

    def hysteresisTabUI(self):
        hysteresis_tab = QWidget()
        widgets = app_widgets.WidgetsForApp()

        outer_layout   = QVBoxLayout()
        v_outer_layout = QVBoxLayout()
        h_outer_layout = QHBoxLayout()

        hyst_layout    = QVBoxLayout()
        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()

        # plt = pg.plot()
        # hyst_layout.addWidget(plt)
        hyst_layout.addWidget(self.graph_widget)

        # plt.addLegend()
        # c1 = plt.plot([1, 3, 2, 4], pen='y', name='Yellow Plot')
        # c2 = plt.plot([2, 1, 4, 3], pen='b', fillLevel=0, fillBrush=(255, 255, 255, 30), name='Blue Plot')
        # c3 = plt.addLine(y=4, pen='y')

        # temp_layout = QVBoxLayout()
        # temp_layout.addWidget(widgets.plotWidget)

        top_layout.addWidget(widgets.lbl_COM,           0, 0, Qt.AlignCenter)
        top_layout.addWidget(widgets.cb_COM,            0, 1)
        top_layout.addWidget(widgets.btn_IDN,           1, 0)
        top_layout.addWidget(self.twin_le_IDN,            1, 1)

        middle_layout.addWidget(widgets.lbl_I_start,    2, 1, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_I_stop,     0, 1, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_volt,       2, 2, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_amper,      0, 2, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_step,       2, 0, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_loops,      0, 0, Qt.AlignCenter)
        middle_layout.addWidget(widgets.lbl_resistance, 0, 3, Qt.AlignCenter)

        middle_layout.addWidget(widgets.le_amper,       1, 2)
        middle_layout.addWidget(widgets.le_volt,        3, 2)
        middle_layout.addWidget(widgets.le_resistance,  1, 3)

        middle_layout.addWidget(widgets.dsb_I_start,    3, 1)
        middle_layout.addWidget(widgets.dsb_I_stop,     1, 1)
        middle_layout.addWidget(widgets.dsb_step,       3, 0)
        middle_layout.addWidget(widgets.sb_loops,       1, 0, Qt.AlignCenter)

        bottom_layout.addWidget(widgets.btn_start,      0, 0)
        bottom_layout.addWidget(widgets.btn_stop,       0, 1)
        bottom_layout.addWidget(widgets.btn_reset,      1, 0)
        bottom_layout.addWidget(widgets.btn_start_meas, 1, 1)
        bottom_layout.addWidget(widgets.btn_open,       2, 0)
        bottom_layout.addWidget(widgets.btn_save,       2, 1)

        # widgets.hysteresis.setLayout(temp_layout)
        hyst_layout.addWidget(widgets.hysteresis)

        # All connections
        widgets.btn_IDN.clicked.connect(self.on_clicked_btn_IDN)
        widgets.btn_start.clicked.connect(self.on_clicked_btn_start)
        widgets.btn_stop.clicked.connect(self.on_clicked_btn_stop)
        widgets.btn_reset.clicked.connect(self.on_clicked_btn_reset)
        widgets.btn_start_meas.clicked.connect(self.on_clicked_btn_start_meas)
        widgets.btn_open.clicked.connect(self.on_clicked_btn_open)
        # widgets.btn_save.clicked.connect(self.on_clicked_btn_save)
        self.port.readyRead.connect(self.read_from_port)


        widgets.box_1.setLayout(top_layout)
        widgets.box_2.setLayout(middle_layout)
        widgets.box_3.setLayout(bottom_layout)
        widgets.box_4.setLayout(hyst_layout)

        h_outer_layout.addLayout(v_outer_layout)

        v_outer_layout.addWidget(widgets.box_1)
        v_outer_layout.addWidget(widgets.box_2)
        v_outer_layout.addWidget(widgets.box_3)
        h_outer_layout.addWidget(widgets.box_4)
        outer_layout.addLayout(v_outer_layout)
        outer_layout.addLayout(h_outer_layout)

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
        layout.addWidget(widgets.cb_flow_control)
        layout.addWidget(widgets.btn_open_serial_data)

        widgets.btn_open_serial_data.clicked.connect(self.on_clicked_btn_open_serial_data)

        configure_tab.setLayout(layout)

        return configure_tab

    def port_write(self, flag):
        widgets = app_widgets.WidgetsForApp()
        if flag:
            self.port.setBaudRate(widgets.cb_baud_rates())
            self.port.setPortName(widgets.cb_port_names())
            self.port.setDataBits(widgets.cb_data_bits())
            self.port.setParity(widgets.cb_parity())
            self.port.setStopBits(widgets.cb_stop_bits())
            self.port.setFlowControl(widgets.cb_flow_control())
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


    def serialControlEnable(self, flag):
        widgets = app_widgets.WidgetsForApp()

        widgets.cb_port_names.setEnabled(flag)
        widgets.cb_baud_rates.setEnabled(flag)
        widgets.cb_data_bits.setEnabled(flag)
        widgets.cb_parity.setEnabled(flag)
        widgets.cb_stop_bits.setEnabled(flag)
        widgets.cb_flow_control.setEnabled(flag)

    def baudRate(self):
        widgets = app_widgets.WidgetsForApp()
        return int(widgets.cb_baud_rates.currentText())

    def portName(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_port_names.currentText()

    def dataBit(self):
        widgets = app_widgets.WidgetsForApp()
        return int(widgets.cb_data_bits.currentIndex() + 5)

    def parity(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_parity.currentIndex()

    def stopBit(self):
        widgets = app_widgets.WidgetsForApp()
        a = 'text'
        return a
        # return widgets.cb_stop_bits.currentIndex()

    def flowControl(self):
        widgets = app_widgets.WidgetsForApp()
        return widgets.cb_flow_control.currentIndex()

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
        widgets = app_widgets.WidgetsForApp()
        if not QSerialPortInfo.availablePorts():
            self.status_text.setText(" no ports ")
            widgets.btn_save.setCheckable(True)
        else:
            self.port.setPortName(widgets.cb_COM.currentText())
            self.port.setBaudRate(int(widgets.cb_baud_rates.currentText()))
            self.port.setParity(widgets.cb_parity.currentIndex())
            self.port.setDataBits(int(widgets.cb_data_bits.currentIndex() + 5))
            self.port.setFlowControl(widgets.cb_flow_control.currentIndex())
            self.port.setStopBits(widgets.cb_stop_bits.currentIndex())
            ready = self.port.open(QIODevice.ReadWrite)
            if not ready:
                self.status_text.setText("Port open error")
                widgets.btn_IDN.setChecked(False)
                self.serialControlEnable(True)
            else:
                self.status_text.setText("Port opened")
                self.serialControlEnable(False)
        # self.port.close()
        # self.status_text.setText("Port closed")
        # self.serialControlEnable(True)


    def on_clicked_btn_open_serial_data(self):
        self.window = app_widgets.newWindow()
        self.window.show()

    # def appendSerialText(self, appendText):
    #     widgets = app_widgets.WidgetsForApp()
    #     widgets.serial_data.setText(appendText)
    #     Text = appendText.encode()

    def on_clicked_btn_IDN(self):
        widgets = app_widgets.WidgetsForApp()

        self.init_port()
        self.port.write("A007*IDN?\n".encode())

    def read_from_port(self):
        data = self.port.read(33)
        self.twin_le_IDN.setText(str(data.rstrip()))



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

    def on_clicked_btn_start(self):
        pass

    def on_clicked_btn_stop(self):
        pass

    def on_clicked_btn_reset(self):
        pass

    def on_clicked_btn_start_meas(self):
        pass

    def on_clicked_btn_open(self):
        pass

    # def on_clicked_btn_save(self):
    #     print()

    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.
        self.data_line.setData(self.x, self.y)  # Update the data.

    def onMouseClicked(self, event):
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()
        self.status_text.setText("Coordinates of the point: x = {}, y = {}".format(x, y))

