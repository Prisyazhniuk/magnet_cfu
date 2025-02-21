import os
import sys
import time
import numpy as np
import pyqtgraph as pg

from contextlib import contextmanager
from pathlib import Path
from zhinst.toolkit import Session
from zhinst.core import ziListEnum, ziDiscovery, ziDAQServer
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
    QComboBox,
    QSplitter,
    QFrame
)


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def rev_decimal_range(start, stop, increment):
    while start > stop:
        yield start
        start -= increment


class MagnetCFU(QMainWindow):
    version_app = '0.1.4'
    date_build  = '21.02.2025'

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.port            = QSerialPort()
        self.graph_layout    = pg.GraphicsLayoutWidget()
        self.lock_in_plot    = self.graph_layout.addPlot(row=1, col=0)
        self.hysteresis_plot = self.graph_layout.addPlot(row=2, col=0)
        self.timer_lock_in   = QTimer()

        self.timer_lock_in.timeout.connect(self.update_lock_in_data)
        self.timer_lock_in.setInterval(10)

        # upd_freq = pyqtSignal(str)  # возможно, надо удалить
        # self.graph_widget     = pg.PlotWidget()
        # self.lock_in_gw       = pg.PlotWidget()
        # self.hysteresis_graph = pg.PlotWidget()

        self.time_window = 10
        self.max_history = 1000
        self.data_buffer = {}

        # self.timer_mang       = QTimer()
        # self.upd_freq_timer   = QTimer()

        self.real_curr        = None
        self.real_volt        = None
        self.buffer           = bytearray()
        self.discovery        = ziDiscovery()
        self.device           = self.discovery.find('mf-dev4999').lower()

        # device setup
        self.api_lvl          = 6
        self.dev_prop         = self.discovery.get(self.device)
        self.serveraddress    = self.dev_prop['serveraddress']
        self.serverport       = self.dev_prop['serverport']
        self.serverversion    = self.dev_prop["serverversion"]
        self.daq              = ziDAQServer(self.serveraddress, self.serverport, self.api_lvl)
        self.daq_module       = self.daq.dataAcquisitionModule()

        self.daq.unsubscribe("*")

        # plot lock-in graph
        self.demod_path       = f"/{self.device}/demods/0/sample"  # Continuous equidistantly spaced data in time
        self.signal_paths     = []
        self.filename: str    = ""
        self.plot: bool       = True
        self.data_dev         = {}

        self._setup_plots()
        self.signal_paths.append(self.demod_path + ".x")
        self.signal_paths.append(self.demod_path + ".y")

        # for debug
        self.output_test = ''

        # Check the device has demodulators.
        flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
        streaming_nodes = self.daq.listNodes(self.device, flags)
        if self.demod_path not in (node.lower() for node in streaming_nodes):
            print(
                "Device dev4999 does not have demodulators. Please modify the example to specify",
                "a valid signal_path based on one or more of the following streaming nodes: ",
                "\n".join(streaming_nodes),
            )
            raise Exception(
                "Demodulator streaming nodes unavailable - see the message above for more information."
            )

        # self.daq.subscribe(self.demod_path)
        #
        # sampling_rate = self.daq.getDouble(f"/{self.device}/demods/0/rate")
        # TC = self.daq.getDouble(f"/{self.device}/demods/0/timeconstant")
        #
        # # Without getAsEvent no value would be returned by poll.
        # self.daq.getAsEvent('/dev4999/sigouts/0/amplitudes')
        # self.daq.subscribe('/dev4999/sigouts/0/amplitudes')
        # self.daq.poll(0.200, 10, 0, True)
        #
        # print( sampling_rate)


        #
        #     # Defined the total time we would like to record data for and its sampling rate.
        #     # total_duration: Time in seconds: This examples stores all the acquired data in the `data`
        #     # dict - remove this continuous storing in read_data_update_plot before increasing the size
        #     # of total_duration!
        # total_duration = 2
        # module_sampling_rate = 3000  # Number of points/second
        # burst_duration = 0.2  # Time in seconds for each data burst/segment.
        # num_cols = int(np.ceil(module_sampling_rate * burst_duration))
        # num_bursts = int(np.ceil(total_duration / burst_duration))
        # #
        # # # Configure the Data Acquisition Module.
        # # # Set the device that will be used for the trigger - this parameter must be set.
        # self.daq_module.set("device", self.device)
        # #
        # # # Specify continuous acquisition (type=0).
        # self.daq_module.set("type", 0)
        # # self.daq_module.set("endless", 1)
        #
        # # 'grid/mode' - Specify the interpolation method of
        # #   the returned data samples.
        # #
        # # 1 = Nearest. If the interval between samples on the grid does not match
        # #     the interval between samples sent from the device exactly, the nearest
        # #     sample (in time) is taken.
        # #
        # # 2 = Linear interpolation. If the interval between samples on the grid does
        # #     not match the interval between samples sent from the device exactly,
        # #     linear interpolation is performed between the two neighbouring
        # #     samples.
        # #
        # # 4 = Exact. The subscribed signal with the highest sampling rate (as sent
        # #     from the device) defines the interval between samples on the DAQ
        # #     Module's grid. If multiple signals are subscribed, these are
        # #     interpolated onto the grid (defined by the signal with the highest
        # #     rate, "highest_rate"). In this mode, duration is
        # #     read-only and is defined as num_cols/highest_rate.
        # self.daq_module.set("grid/mode", 2)
        # # 'count' - Specify the number of bursts of data the
        # #   module should return (if endless=0). The
        # #   total duration of data returned by the module will be
        # #   count*duration.
        # self.daq_module.set("count", num_bursts)
        # # 'duration' - Burst duration in seconds.
        # #   If the data is interpolated linearly or using nearest neighbout, specify
        # #   the duration of each burst of data that is returned by the DAQ Module.
        # self.daq_module.set("duration", burst_duration)
        # # 'grid/cols' - The number of points within each duration.
        # #   This parameter specifies the number of points to return within each
        # #   burst (duration seconds worth of data) that is
        # #   returned by the DAQ Module.
        # self.daq_module.set("grid/cols", num_cols)
        #
        # if self.filename:
        #     # 'save/fileformat' - The file format to use for the saved data.
        #     #    0 - Matlab
        #     #    1 - CSV
        #     self.daq_module.set("save/fileformat", 1)
        #     # 'save/filename' - Each file will be saved to a
        #     # new directory in the Zurich Instruments user directory with the name
        #     # filename_NNN/filename_NNN/
        #     self.daq_module.set("save/filename", self.filename)
        #     # 'save/saveonread' - Automatically save the data
        #     # to file each time read() is called.
        #     self.daq_module.set("save/saveonread", 1)


        # A dictionary to store all the acquired data.
        # for signal_path in self.signal_paths:
        #     print("Subscribing to ", signal_path)
        #     self.daq_module.subscribe(signal_path)
        #     self.data_dev[signal_path] = []

        self.clockbase = float(self.daq.getInt(f'/{self.device}/clockbase'))
        #
        #     ts0 = np.nan
        #     self.read_count = 0

        # # Start recording data.
        # self.daq_module.execute()
        # #
        # # # Record data in a loop with timeout.
        # timeout = 1.5 * total_duration
        # t0_measurement = time.time()
        # # The maximum time to wait before reading out new data.
        # t_update = 0.9 * burst_duration
        # while not self.daq_module.finished():
        #     t0_loop = time.time()
        #     if time.time() - t0_measurement > timeout:
        #         raise Exception(
        #             f"Timeout after {timeout} s - recording not complete."
        #             "Are the streaming nodes enabled?"
        #             "Has a valid signal_path been specified?"
        #         )
        #     self.data_dev, ts0 = self.read_data_update_plot(self.data_dev, ts0)
        #     self.read_count += 1
        #     # We don't need to update too quickly.
        #     time.sleep(max(0, t_update - (time.time() - t0_loop)))
        # #
        # # There may be new data between the last read() and calling finished().
        # self.data_dev, _ = self.read_data_update_plot(self.data_dev, ts0)
        #
        # # Before exiting, make sure that saving to file is complete (it's done in the background)
        # # by testing the 'save/save' parameter.
        # timeout = 1.5 * total_duration
        # t0 = time.time()
        # while self.daq_module.getInt("save/save") != 0:
        #     time.sleep(0.1)
        #     if time.time() - t0 > timeout:
        #         raise Exception(f"Timeout after {timeout} s before data save completed.")
        #
        # if not self.plot:
        #     print("Please run with `plot` to see dynamic plotting of the acquired signals.")

        self.start_continuous_plotting()

# ----------------------------------------------------------------------------------------------------------------------

        # Creating interface elements | Control tab
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

        self.box_01         = QGroupBox("Info")
        self.box_02         = QGroupBox("Value")
        self.box_03         = QGroupBox("Control")
        # self.box_04         = QGroupBox("Hysteresis")
        self.box_lock_in    = QGroupBox("Lock-in")

        self.lbl_volt.setFixedSize(45, 40)
        self.lbl_amper.setFixedSize(45, 40)

        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_step.setRange(0.01, 0.05)

        self.dsb_I_start.setSingleStep(0.01)
        self.dsb_I_stop.setSingleStep(0.01)
        self.dsb_step.setSingleStep(0.01)

        self.sb_loops.setValue(1)
        self.sb_loops.setFixedSize(45, 35)
        self.sb_interval.setSingleStep(100)
        self.sb_interval.setRange(0, 10000)
        self.sb_interval.setValue(1000)

        self.sb_interval.setFixedSize(100, 35)
        self.le_resistance.setFixedSize(100, 35)

        self.le_IDN.setReadOnly(1)

        self.le_volt.setPlaceholderText("0.00")
        self.le_amper.setPlaceholderText("0.00")

        for i in [self.dsb_step, self.dsb_I_stop, self.dsb_I_start, self.le_volt, self.le_amper]:
            i.setFixedSize(70, 35)

        self.cb_COM.setFixedSize(90, 35)
        self.btn_IDN.setFixedWidth(70)
        self.le_IDN.setFixedHeight(26)

        for i in [self.le_amper, self.le_volt, self.le_resistance]:
            i.setDisabled(True)

        for i in [self.btn_set_curr, self.btn_reset, self.btn_start_meas]:
            i.setCheckable(True)

        for i in [self.dsb_I_start, self.dsb_I_stop, self.lbl_amper, self.lbl_volt, self.dsb_step, self.sb_loops,
                  self.sb_interval, self.le_IDN, self.le_volt, self.le_amper, self.le_resistance]:
            i.setAlignment(Qt.AlignCenter)

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
        elif self.cb_COM.count() > 0:
            self.cb_COM.setCurrentText('COM4')
        else:
            self.cb_COM.setCurrentIndex(0)

        # Window setting
        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")
        self.setContentsMargins(1, 1, 1, 1)

        container     = QWidget()
        bottom_sp     = QWidget()
        tabs          = QTabWidget()
        outer_vlayout = QVBoxLayout()
        outer_hlayout = QHBoxLayout()
        hyst_outer    = QVBoxLayout()
        # hyst_layout   = QVBoxLayout()
        lock_in       = QVBoxLayout()
        top_layout    = QGridLayout()
        middle_layout = QGridLayout()
        bottom_layout = QGridLayout()

        # bottom_sp.setFixedSize(100, 130)

        # hyst_layout.addWidget(self.hysteresis_graph)
        lock_in.addWidget(self.graph_layout)
        # lock_in.addWidget(self.lock_in_gw)

        # self.box_04.setFixedSize(500, 300)
        # self.box_04.setLayout(hyst_layout)
        # self.box_lock_in.setFixedSize(500, 300)
        self.box_lock_in.setLayout(lock_in)

        # hyst_outer.addWidget(self.box_04)
        hyst_outer.addWidget(self.box_lock_in)
        # hyst_outer.addWidget(bottom_sp)

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
        self.btn_IDN.clicked.connect       (self.on_btn_idn)
        self.btn_set_curr.clicked.connect  (self.on_btn_set_curr)
        self.btn_stop.clicked.connect      (self.on_btn_stop)
        self.btn_reset.clicked.connect     (self.on_btn_reset)
        self.btn_start_meas.clicked.connect(self.on_btn_start_meas)
        self.btn_open.clicked.connect      (self.on_btn_open)

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

        for i in [self.lbl_baud_rates, self.cb_baud_rates, self.lbl_data_bits, self.cb_data_bits, self.lbl_parity,
                  self.cb_parity, self.lbl_stop_bits, self.cb_stop_bits, self.lbl_flow_control, self.cb_flow_control]:
            layout.addWidget(i)

        for i in [self.cb_baud_rates, self.cb_data_bits, self.cb_parity, self.cb_stop_bits, self.cb_flow_control]:
            i.setFixedSize(120, 40)

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
        v_bottom_layout  = QVBoxLayout()
        h1_outer_layout  = QHBoxLayout()
        h2_outer_layout  = QHBoxLayout()

        top_layout       = QGridLayout()
        middle_layout    = QGridLayout()
        bottom_layout    = QGridLayout()
        middle_rlayout   = QGridLayout()

        self.le_device   = QLineEdit()
        self.le_host     = QLineEdit()
        self.le_port     = QLineEdit()
        self.le_version  = QLineEdit()

        if self.serveraddress == "172.16.0.35":
            self.status_text.setText("MFLI connected global")

            self.le_host.setText(self.serveraddress)
            self.le_port.setText(str(self.serverport))
            self.le_version.setText(str(self.serverversion))

            self.le_device.setText(self.dev_prop['devicetype'] + " " + self.dev_prop['deviceid'])

        elif self.serveraddress == "127.0.0.1":
            self.status_text.setText("MFLI connected local")
            daq = ziDAQServer(self.serveraddress, self.serverport, 6)

            self.le_host.setText(self.serveraddress)
            self.le_port.setText(str(self.serverport))
            self.le_version.setText(str(self.serverversion))

            self.le_device.setText(self.dev_prop['devicetype'] + " " + self.dev_prop['deviceid'])

        else:
            self.status_text.setText("MFLI not found")

        self.box_06       = QGroupBox("Lock-in")
        self.box_07       = QGroupBox("Demodulators")
        self.box_08       = QGroupBox("Signal Inputs")
        self.box_09       = QGroupBox("Signal Outputs")
        self.box_10       = QGroupBox()

        # Lock-in GroupBox
        self.lbl_wserver  = QLabel("<b>Data Server</b>")
        self.lbl_device   = QLabel("Device")
        self.lbl_host     = QLabel("Host")
        self.lbl_sport    = QLabel("Port")
        self.lbl_sversion = QLabel("Version")

        for i in [self.lbl_device, self.lbl_wserver, self.lbl_sversion, self.lbl_host, self.lbl_sport]:
            i.adjustSize()

        self.box_07.setFixedHeight(400)

        for i in [self.le_host, self.le_port, self.le_version, self.le_device]:
            i.setFixedHeight(35)

        for i in [self.le_host, self.le_port, self.le_version, self.le_device]:
            i.setDisabled(True)

        # Demodulators GroupBox
        self.lbl_freq     = QLabel("Freq (Hz)")
        self.lbl_sig_in   = QLabel("Sig In")
        self.lbl_phase    = QLabel("Phase (deg)")
        self.lbl_transfer = QLabel("Data Transfer")
        self.lbl_trigger  = QLabel("Trigger")
        self.lbl_tc       = QLabel("TC")
        self.lbl_order    = QLabel("Order")

        self.le_freq      = QLineEdit()
        self.le_tc        = QLineEdit("0.1")
        self.le_phase     = QLineEdit("90.0")
        self.le_transfer  = QLineEdit("1674")

        self.btn_phase    = QPushButton("Auto")
        self.btn_transfer = QPushButton("Auto")

        self.cb_order     = QComboBox()
        self.cb_trigger   = QComboBox()

        self.le_freq.setDisabled(True)

        self.le_transfer.setAlignment(Qt.AlignRight)
        self.le_phase.setAlignment(Qt.AlignRight)

        for i in [self.le_freq, self.le_transfer, self.le_phase, self.le_tc, self.cb_order, self.cb_trigger]:
            i.setFixedHeight(30)

        self.cb_trigger.addItems(['Continuous', 'Trigger In 1', 'Trigger In 2', 'Trigger In 1|2'])

        for i in range(1, 9):
            self.cb_order.addItem(str(i))
        self.cb_order.setCurrentIndex(3)

        self.btn_transfer.setCheckable(True)
        self.btn_transfer.setChecked(True)

        # Signal Inputs GroupBox
        self.lbl_range   = QLabel("Range")
        self.lbl_scaling = QLabel("Scaling")

        self.le_range    = QLineEdit("3.0")
        self.le_scaling  = QLineEdit("1.0")

        self.btn_range   = QPushButton("Auto")
        self.btn_ac      = QPushButton("AC")
        self.btn_50      = QPushButton("50 Ω")
        self.btn_float   = QPushButton("Float")

        self.cb_sigin    = QComboBox()
        self.cb_sigin.setFixedHeight(30)
        for i in ['Sig In 1', 'Curr In 1', 'Trigger 1', 'Trigger 2', 'Aux Out 1', 'Aux Out 2']:
            self.cb_sigin.addItem(i)

        for i in [self.btn_float, self.btn_ac, self.btn_50]:
            i.setCheckable(True)

        self.btn_ac.setChecked(True)
        self.btn_50.setChecked(True)

        self.btn_float.setFixedWidth(50)
        self.btn_range.setFixedWidth(50)
        self.btn_50.setFixedWidth(50)
        self.btn_ac.setFixedWidth(40)

        self.le_range.setFixedSize(50, 30)
        self.le_range.setAlignment(Qt.AlignRight)
        self.le_scaling.setFixedSize(50, 30)
        self.le_scaling.setAlignment(Qt.AlignRight)

        # Signal Outputs GroupBox
        self.lbl_orange     = QLabel("Range")
        self.lbl_amp        = QLabel("Amp (Vpk)")

        self.cb_orange      = QComboBox()
        self.le_amp         = QLineEdit("0.100")

        self.btn_output_sig = QPushButton("On")
        self.btn_auto_amp   = QPushButton("Auto")

        self.btn_auto_amp.setCheckable(True)
        self.btn_auto_amp.setChecked(True)

        self.le_amp.setFixedHeight(30)
        self.le_amp.setAlignment(Qt.AlignRight)

        self.cb_orange.addItems(['10 mV', '100 mV', '1 V', '10 V'])
        self.cb_orange.setCurrentIndex(2)
        self.cb_orange.setFixedHeight(30)

        # Connect lock-in button
        self.le_freq.setMaxLength(13)

        # self.upd_freq_timer.setInterval(500)
        # self.upd_freq_timer.timeout.connect(self.changed_freq)
        # self.upd_freq_timer.start()
        #
        # QTimer.singleShot(5000, self.stop_selection)

        self.le_range.textChanged.connect        (self.changed_range)
        self.le_scaling.textChanged.connect      (self.changed_scaling)
        self.le_phase.textChanged.connect        (self.changed_phase)
        self.le_transfer.textChanged.connect     (self.changed_transfer)
        self.le_tc.textChanged.connect           (self.changed_tc)
        self.le_amp.editingFinished.connect      (self.changed_amp)

        self.cb_order.currentIndexChanged.connect(self.changed_order)

        self.btn_float.clicked.connect           (self.on_clicked_btn_float)
        self.btn_ac.clicked.connect              (self.on_clicked_btn_ac)
        self.btn_50.clicked.connect              (self.on_clicked_btn_50)
        self.btn_range.clicked.connect           (self.on_clicked_btn_range)
        self.btn_transfer.clicked.connect        (self.on_clicked_btn_transfer)
        self.btn_auto_amp.clicked.connect        (self.on_clicked_btn_auto_amp)
        self.btn_phase.clicked.connect           (self.on_clicked_btn_phase)

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
        middle_layout.addWidget(self.lbl_sig_in,     4, 1)
        middle_layout.addWidget(self.lbl_tc,         4, 0)
        middle_layout.addWidget(self.lbl_order,      2, 0)

        middle_layout.addWidget(self.le_phase,       1, 1)
        middle_layout.addWidget(self.le_freq,        1, 0)
        middle_layout.addWidget(self.le_transfer,    3, 1)
        middle_layout.addWidget(self.le_tc,          5, 0)

        middle_layout.addWidget(self.cb_trigger,     7, 0)
        middle_layout.addWidget(self.cb_order,       3, 0)
        middle_layout.addWidget(self.cb_sigin,       5, 1)

        middle_layout.addWidget(self.btn_phase,      1, 2)
        middle_layout.addWidget(self.btn_transfer,   3, 2)

        bottom_layout.addWidget(self.lbl_range,      0, 0)
        bottom_layout.addWidget(self.le_range,       0, 1)
        bottom_layout.addWidget(self.btn_range,      0, 2)
        bottom_layout.addWidget(self.lbl_scaling,    1, 0)
        bottom_layout.addWidget(self.le_scaling,     1, 1)
        bottom_layout.addWidget(self.btn_ac,         2, 0)
        bottom_layout.addWidget(self.btn_50,         2, 2)
        bottom_layout.addWidget(self.btn_float,      2, 1)

        # Output Sig
        middle_rlayout.addWidget(self.lbl_orange,     0, 1, Qt.AlignRight)
        middle_rlayout.addWidget(self.cb_orange,      0, 2)
        middle_rlayout.addWidget(self.lbl_amp,        1, 0)
        middle_rlayout.addWidget(self.le_amp,         1, 1)
        middle_rlayout.addWidget(self.btn_output_sig, 0, 0)
        middle_rlayout.addWidget(self.btn_auto_amp,   1, 2)

        bottom_layout.setAlignment(Qt.AlignLeft)

        self.box_06.setLayout(top_layout)
        self.box_07.setLayout(middle_layout)
        self.box_09.setLayout(middle_rlayout)
        self.box_08.setLayout(bottom_layout)

        h1_outer_layout.addWidget(self.box_06)
        h1_outer_layout.addWidget(self.box_08)

        v_bottom_layout.addWidget(self.box_09)
        v_bottom_layout.addWidget(self.box_10)

        h2_outer_layout.addWidget(self.box_07)
        h2_outer_layout.addLayout(v_bottom_layout)

        outer_layout.addLayout(h1_outer_layout)
        outer_layout.addLayout(h2_outer_layout)

        _lock_in_tab.setLayout(outer_layout)
        return _lock_in_tab

    def stop_selection(self):
        print(str(self.daq.getDouble(f'/{self.device}/oscs/0/freq')))

    def on_clicked_btn_float(self):
        if self.btn_float.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/float', 1)
        elif not self.btn_float.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/float', 0)

    def on_clicked_btn_50(self):
        if self.btn_50.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/imp50', 1)
        elif not self.btn_50.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/imp50', 0)

    def on_clicked_btn_ac(self):
        if self.btn_ac.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/ac', 1)
        elif not self.btn_ac.isChecked():
            self.daq.setInt(f'/{self.device}/sigins/0/ac', 0)

    def on_clicked_btn_range(self):
        self.daq.setInt(f'/{self.device}/sigins/0/autorange', 1)

    def on_clicked_btn_transfer(self):
        if self.btn_transfer.isChecked():
            self.daq.setInt(f'/{self.device}/demods/0/enable', 1)
        elif not self.btn_transfer.isChecked():
            self.daq.setInt(f'/{self.device}/demods/0/enable', 0)

    def on_clicked_btn_auto_amp(self):
        if self.btn_auto_amp.isChecked():
            self.daq.setInt(f'/{self.device}/sigouts/0/enables/1', 1)
        elif not self.btn_auto_amp.isChecked():
            self.daq.setInt(f'/{self.device}/sigouts/0/enables/1', 0)

    def on_clicked_btn_phase(self):
        self.daq.setInt(f'/{self.device}/demods/0/phaseadjust', 1)
        self.le_phase.setText(str(self.daq.getDouble('/dev4999/demods/0/phaseshift')))
        self.le_phase.setMaxLength(6)

    def changed_range(self):
        self.daq.setDouble(f'/{self.device}/sigins/0/range', float(self.le_range.text()))

    def changed_scaling(self):
        self.daq.setDouble(f'/{self.device}/sigins/0/scaling', float(self.le_scaling.text()))

    def changed_transfer(self):
        self.daq.setDouble(f'/{self.device}/demods/0/rate', float(self.le_transfer.text()))

    def changed_phase(self):
        self.daq.setDouble(f'/{self.device}/demods/0/phaseshift', float(self.le_phase.text()))

    def changed_order(self):
        self.daq.setInt(f'/{self.device}/demods/0/order', int(self.cb_order.currentText()))

    def changed_tc(self):
        self.daq.setDouble(f'/{self.device}/demods/0/timeconstant', float(self.le_tc.text()))

    def changed_amp(self):
        self.daq.setDouble(f'/{self.device}/sigouts/0/amplitudes/1', float(self.le_amp.text()))

    def changed_freq(self):
        self.le_freq.setText(str(self.daq.getDouble(f'/{self.device}/oscs/0/freq')))

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

    def init_port(self):
        if not QSerialPortInfo.availablePorts():
            self.status_text.setText("no ports")

        self.port.setPortName(self.cb_COM.currentText())
        self.port.setBaudRate(int(self.cb_baud_rates.currentText()))
        self.port.setParity(self.cb_parity.currentIndex())
        self.port.setDataBits(int(self.cb_data_bits.currentIndex() + 5))
        self.port.setFlowControl(self.cb_flow_control.currentIndex())
        self.port.setStopBits(self.cb_stop_bits.currentIndex())

        if not self.port.open(QIODevice.ReadWrite):
            self.status_text.setText("Port open error")
            # self.serial_control_enable(True) # если код работает, удалить всю функцию
            return False

        self.status_text.setText("Remote control completed")
        return True

    @contextmanager
    def open_port(self):
        if not self.init_port():
            raise Exception("Can't open port")
        try:
            yield
        finally:
            self.port.close()
            self.status_text.setText("Port closed")

    def send_command(self, command):
        self.port.write(command.encode())
        self.port.waitForReadyRead(self.sb_interval.value())
        data = self.port.readAll()
        decode_data = data.data().decode()
        return decode_data.rstrip('\r\n')

        # another realization read port
        # if self.port.canReadLine():
        #     idn_text = self.port.readLine().data().decode()[2:]
        #     self.le_IDN.setText(idn_text)
        # else:
        #     self.status_text.setText("Can't read IDN")

    def send_commands(self, data):
        for value in data:
            self.port.writeData(value.encode())
            self.port.waitForReadyRead(self.sb_interval.value())

    # def write_port(self, data):
    #     self.port.writeData(data.encode())
    #
    # def write_port_list(self, data):
    #     for value in data:
    #         self.port.writeData(value.encode())

    @pyqtSlot()
    def on_btn_idn(self):
        with self.open_port():
            self.le_IDN.setText(self.send_command("A007*IDN?\n")[2:])

            # volt, amper = self.read_measurements()
            # self.le_volt.setText(f"{volt: .2f}")
            # self.le_amper.setText(f"{amper: .2f}")

            volt, amper = self.read_volt_amper()
            self.le_volt.setText(f"{volt}")
            self.le_amper.setText(f"{amper}")

    # def read_volt_and_amper(self):
    #     volt = float(self.send_command("A007MEAS:VOLT?\n"))
    #     amper = float(self.send_command("A007MEAS:CURR?\n"))
    #     return volt, amper

    def read_volt_amper(self):
        volt, amper = self.send_command("A007FETC?\n").split(',')
        return float(volt), float(amper)

    @pyqtSlot()
    def on_btn_set_curr(self):
        with self.open_port():
            data = ["A007SYST:REM\n", "A007*CLS\n", "A007OUTP ON\n"]
            self.send_commands(data)
            self.set_current(0,
                             abs(self.dsb_I_start.value()) + self.dsb_step.value(),
                             self.dsb_step.value(),
                             2 if self.dsb_I_start.value() < 0 else 1)

    def set_current(self, start, stop, step, polarity):
        self.send_command(f"*POL {polarity}\n")
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        for current in decimal_range(start, stop, step):
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.send_command(f"A007SOUR:VOLT {current * 10:.3f};CURR {current:.3f}\n")
        self.btn_set_curr.setChecked(False)

    @pyqtSlot()
    def on_btn_stop(self):
        pass

    @pyqtSlot()
    def on_btn_reset(self):
        with self.open_port():
            data = ["A007SYST:REM\n", "A007*CLS\n", "A007OUTP ON\n"]
            self.send_commands(data)
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            self.reset_current(abs(self.dsb_I_start.value()) - self.dsb_step.value(),
                               -self.dsb_step.value(),
                               self.dsb_step.value(),
                               2 if self.dsb_I_start.value() < 0 else 1)
            self.port.waitForReadyRead(self.sb_interval.value() // 2)
            data = ["*POL 1\n", "A007OUTP OFF\n", "A007*RST\n"]
            self.send_commands(data)
        self.status_text.setText("Port closed")
        self.btn_reset.setChecked(False)

    def reset_current(self, start, stop, step, polarity):
        self.send_command(f"*POL {polarity}\n")
        self.port.waitForReadyRead(self.sb_interval.value() // 2)
        for current in rev_decimal_range(start, stop, step):
            if current > 0.05:
                self.port.waitForReadyRead(self.sb_interval.value() // 2)
                self.send_command(f"A007SOUR:VOLT {current * 10:.3f};CURR {current:.3f}\n")
                current -= 0.05
            else:
                self.port.waitForReadyRead(self.sb_interval.value() // 2)
                self.send_command(f"A007SOUR:VOLT {current * 10:.3f};CURR {current:.3f}\n")

        self.btn_set_curr.setChecked(False)


        # self.init_port()
        # if self.dsb_I_start.value() > 0:
        #     for _i in rev_decimal_range(self.dsb_I_start.value() - self.dsb_step.value(),
        #                                 0 - self.dsb_step.value(), self.dsb_step.value()):
        #         self.receive_port()
        #         a = "A007SOUR:VOLT "
        #         b = _i * 10
        #         c = "CURR "
        #         d = _i
        #         res = f"{a}{b:.3f};{c}{d:.3f}\n"
        #         self.port.write(res.encode())
        #
        #     self.port.waitForReadyRead(self.sb_interval.value() // 2)
        #     self.port.write("*POL 1\n".encode())
        #     self.port.waitForReadyRead(self.sb_interval.value() // 2)
        #     self.port.write("A007OUTP OFF\n".encode())
        #     self.port.waitForReadyRead(self.sb_interval.value() // 2)
        #     self.port.write("A007*RST\n".encode())
        #     self.port.close()
        #     self.status_text.setText("Port closed")
        #     self.btn_reset.setChecked(False)
        #
        # elif self.dsb_I_start.value() < 0.0:
        #     for _i in rev_decimal_range(abs(self.dsb_I_start.value()) - self.dsb_step.value(),
        #                                 0 - self.dsb_step.value(), self.dsb_step.value()):
        #         self.receive_port()
        #         a = "A007SOUR:VOLT "
        #         b = _i * 10
        #         c = "CURR "
        #         d = _i
        #         res = f"{a}{b:.3f};{c}{d:.3f}\n"
        #         self.port.write(res.encode())
        #
        #     self.port.waitForReadyRead(self.sb_interval.value() // 2)
        #     self.port.write("*POL 1\n".encode())
        #     self.port.waitForReadyRead(self.sb_interval.value() // 2)
        #     self.port.write("A007OUTP OFF\n".encode())
        #     self.port.write("A007*RST\n".encode())
        #     self.port.close()
        #     self.status_text.setText("Port closed")
        #     self.btn_reset.setChecked(False)

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

    # def read_and_update_data(self):
    #
    #     self.real_curr, self.real_volt = self.get_device_data()
    #
    #     self.hysteresis_graph.plot(self.real_curr, self.real_volt, pen='b', clear=True)

    def get_device_data(self):

        self.timer.start(1000)  # 1000 ms
        
        self.port.write("A007FETC?\n".encode())
        self.port.waitForReadyRead(self.sb_interval.value())
        real_meas_ascii = self.port.readAll()
        real_meas = real_meas_ascii.data().decode().rstrip('\r\n')
        list_real_meas = real_meas.split(',')

        data_v = []
        data_i = []

        data_v.append(float(list_real_meas[0]))
        data_i.append(float(list_real_meas[1]))

        return data_v, data_i



    def start_continuous_plotting(self):

        if not self.daq_module or not self.device:
            raise ValueError("DAQ module или устройство не инициализированы.")

        self.daq_module.set("device", self.device)
        self.daq_module.set("type", 0)  # Непрерывная запись
        self.daq_module.set("endless", 1)
        self.daq_module.set("grid/mode", 2)
        self.daq_module.set("duration", 0.1)  # Продолжительность одного блока (секунды)
        self.daq_module.set("grid/cols", 1)  # Количество точек
        self.daq_module.set("count", 0)  # Непрерывный сбор данных
        self.daq_module.execute()

        # for signal_path in self.signal_paths:
        #     print("Subscribing to ", signal_path)
        #     self.daq_module.subscribe(signal_path)
        #     self.data_dev[signal_path] = []
        #
        # self.timer_lock_in.start()

        # Subscribe to signal paths and initialize data storage
        for signal_path in self.signal_paths:
            signal_path_lower = signal_path.lower()
            print(f"Subscribing to {signal_path}")
            self.daq_module.subscribe(signal_path_lower)
            self.data_dev[signal_path] = []
            # self.data_buffer[signal_path] = {'time': np.array([]), 'values': np.array([])}

        # Ensure timestamp0 is initialized for new acquisition
        self.timestamp0 = None

        # Start the timer for periodic updates
        if hasattr(self, "timer_lock_in"):
            self.timer_lock_in.start()
        else:
            raise AttributeError("Timer для обновления данных не настроен.")

    def update_lock_in_data(self):
        """
        Updates the data in real-time by reading from the DAQ module
        and updating the plot.
        """

        #
        # try:
        #     data_read = self.daq_module.read(flat=True)
        #
        #     for signal_path in self.signal_paths:
        #         signal_data = self.process_signal(data_read, signal_path)
        #
        #         if signal_path not in self.data_buffer:
        #             self.data_buffer[signal_path] = {
        #                 'time': np.array([]),
        #                 'values': np.array([])
        #             }
        #         self.data_buffer[signal_path]['time'] = np.concatenate((
        #             self.data_buffer[signal_path]['time'],
        #             signal_data['time']
        #         ))
        #
        #         self.data_buffer[signal_path]['values'] = np.concatenate((
        #             self.data_buffer[signal_path]['values'],
        #             signal_data['values']
        #         ))
        #
        #         cutoff = self.data_buffer[signal_path]['time'][-1] - self.max_history
        #         mask = self.data_buffer[signal_path]['time'] >= cutoff
        #         self.data_buffer[signal_path]['time'] = self.data_buffer[signal_path]['time'][mask]
        #         self.data_buffer[signal_path]['values'] = self.data_buffer[signal_path]['values'][mask]
        #
        #         if self.plot:
        #             if not hasattr(self, f"data_line_{signal_path}"):
        #                 setattr(self, f"data_line_{signal_path}",
        #                     self.lock_in_plot.plot(pen=pg.mkPen(color='w', width=1.5)))
        #
        #             line = getattr(self, f"data_line_{signal_path}")
        #             line.setData(
        #                 self.data_buffer[signal_path]['time'],
        #                 self.data_buffer[signal_path]['values']
        #             )
        #     if self.auto_scroll:
        #         current_time = self.data_buffer[self.signal_paths[0]]['time'][-1]
        #         self.lock_in_plot.setXRange(current_time - self.time_window, current_time)
        #
        # except Exception as e:
        #     print(f"Error updating plot: {e}")



        try:
            # Ensure timestamp0 is initialized
            if not hasattr(self, "timestamp0"):
                self.timestamp0 = None

            # Read and update data
            self.data_dev, self.timestamp0 = self.read_data_update_plot(self.data_dev, self.timestamp0)

            # Restart the DAQ module if progress indicates completion
            if self.daq_module.progress()[0] >= 1.0:
                self.daq_module.finish()  # Finish the current iteration
                self.daq_module.execute()  # Restart the module for continuous acquisition

        except Exception as e:
            # Stop the timer and report the error
            print(f"Ошибка при обновлении графика: {e}")
            if hasattr(self, "timer_lock_in"):
                self.timer_lock_in.stop()
            raise e

    def stop_continuous_plotting(self):

        if not self.daq_module or not self.device:
            raise ValueError("DAQ module или устройство не инициализированы.")

        self.timer_lock_in.start()

    def read_data_update_plot(self, data_dev, timestamp0, time_window=10):
        """
        Read and process the acquired data, updating the plot as necessary.

        :param data_dev: Данные устройства
        :param timestamp0: Временной ноль для вычитания относительного времени
        :param time_window: Ширина окна отображения данных (в секундах, по умолчанию 10)
        """
        # Read new data from the acquisition module
        data_read = self.daq_module.read(flat=True)
        returned_signal_paths = {signal_path.lower() for signal_path in data_read.keys()}

        # Инициализация хранилища графиков и данных при первом запуске
        if not hasattr(self, "data_lines"):
            self.data_lines = {}  # Хранилище линий графиков (x и y)
            self.data_history = {}  # История накопленных данных (сохраняем массивы времени и значений)

        for signal_path in self.signal_paths:
            signal_path_lower = signal_path.lower()  # Приведение пути к нижнему регистру

            # Проверяем, есть ли данные для текущего пути
            if signal_path_lower not in returned_signal_paths:
                continue

            # Извлекаем данные из возвращенного словаря
            signal_burst = data_read[signal_path_lower][0]

            # Инициализация timestamp0 (если None)
            if timestamp0 is None and "timestamp" in signal_burst:
                timestamp0 = signal_burst["timestamp"][0, 0]

            # Получаем относительное время и значения
            t = (signal_burst["timestamp"][0, :] - timestamp0) / self.clockbase
            values = signal_burst["value"][0, :]

            # Проверяем, что массивы t и values валидны
            if len(values) < 2 or len(t) != len(values):
                raise ValueError(f"Некорректные данные для {signal_path_lower}: длины t и values не совпадают.")

            # Определяем имя графика ('x' или 'y') в зависимости от пути
            if signal_path_lower.endswith(".x"):
                graph_name = "x"
                color = "r"  # Красный для x
            elif signal_path_lower.endswith(".y"):
                graph_name = "y"
                color = "b"  # Синий для y
            else:
                continue  # Игнорируем другие сигналы, если они вдруг появятся

            # Создаем графики, если ещё не существуют
            if graph_name not in self.data_lines:
                # Создаем новую линию данных
                self.data_lines[graph_name] = self.lock_in_plot.plot(
                    [], [],
                    pen=pg.mkPen(color=color, width=2),
                    symbol='o',
                    symbolSize=7,
                    symbolBrush=pg.mkColor(color),
                    name=graph_name
                )
                # Создаем хранилище для данных
                self.data_history[graph_name] = {"t": np.array([]), "values": np.array([])}

            # Обновляем историю накопленных данных
            history = self.data_history[graph_name]
            history["t"] = np.append(history["t"], t)
            history["values"] = np.append(history["values"], values)

            # Обрезаем историю данных, чтобы сохранять только последние time_window секунд
            max_time = history["t"][-1] if len(history["t"]) > 0 else 0
            mask = history["t"] >= max_time - time_window
            history["t"] = history["t"][mask]
            history["values"] = history["values"][mask]

            # Подготавливаем данные для отображения (плавающее окно от -time_window до 0)
            t_display = history["t"] - max_time
            values_display = history["values"]

            # Обновляем данные линии графика
            self.data_lines[graph_name].setData(t_display, values_display)

        # Создание или обновление легенды
        if not hasattr(self, "legend"):
            self.legend = self.lock_in_plot.addLegend()
        else:
            self.legend.clear()

        # Добавляем линии данных в легенду
        for graph_name, line in self.data_lines.items():
            self.legend.addItem(line, graph_name)

        return data_dev, timestamp0
    #
    # def read_data_update_plot(self, data_dev, timestamp0):
    #     """
    #     Read and process the acquired data, updating the plot as necessary.
    #     """
    #     # Read new data from the acquisition module
    #     data_read = self.daq_module.read(flat=True)
    #     returned_signal_paths = {signal_path.lower() for signal_path in data_read.keys()}
    #
    #     # Инициализация линии данных при первом запуске
    #     if not hasattr(self, "data_lines"):
    #         self.data_lines = {}  # Хранилище линий данных для каждого канала
    #
    #     for signal_path in self.signal_paths:
    #         signal_path_lower = signal_path.lower()  # Приведение пути к нижнему регистру
    #
    #         # Проверяем, были ли возвращены данные с текущего пути
    #         if signal_path_lower not in returned_signal_paths:
    #             continue
    #
    #         # Извлечение текущих данных для пути
    #         signal_burst = data_read[signal_path_lower][0]  # Берем первый блок данных
    #
    #         # Инициализация timestamp0, если оно отсутствует
    #         if timestamp0 is None and "timestamp" in signal_burst:
    #             timestamp0 = signal_burst["timestamp"][0, 0]
    #
    #         # Вычисляем временные метки (в секундах) и значения для графика
    #         t = (signal_burst["timestamp"][0, :] - timestamp0) / self.clockbase
    #         values = signal_burst["value"][0, :]  # Значения измерений
    #
    #         # Проверка на валидность данных
    #         if len(values) < 2 or len(t) != len(values):
    #             raise ValueError("Данные некорректны: длина времен t и значений values должна совпадать!")
    #
    #         # Для каждого пути будет только один график `_y1`
    #         key = f"{signal_path_lower}_y1"
    #
    #         # Если линия для текущего пути еще не существует, создаем ее
    #         if key not in self.data_lines:
    #             # Определяем цвет графика в зависимости от пути
    #             if signal_path_lower.endswith(".x"):
    #                 color = "r"  # Красный для `sample.x`
    #             elif signal_path_lower.endswith(".y"):
    #                 color = "b"  # Синий для `sample.y`
    #             else:
    #                 color = "g"  # Зеленый, если случайно попадется другой канал
    #
    #             # Создаем график с выбранным цветом
    #             self.data_lines[key] = self.lock_in_plot.plot(
    #                 [], [],
    #                 pen=pg.mkPen(color=color, width=2),
    #                 symbol='o',
    #                 symbolSize=7,
    #                 symbolBrush=pg.mkColor(color),
    #                 name=f"{signal_path}_y1"
    #             )
    #
    #         # Достаем текущую линию графика для обновления данных
    #         data_line_y1 = self.data_lines[key]
    #
    #         # Обновляем данные для графика
    #         t_data_y1 = np.append(data_line_y1.xData, t)
    #         updated_values = np.append(data_line_y1.yData, values)
    #
    #         # Синхронизируем длины данных
    #         if len(t_data_y1) > len(updated_values):
    #             t_data_y1 = t_data_y1[:len(updated_values)]
    #         elif len(updated_values) > len(t_data_y1):
    #             updated_values = updated_values[:len(t_data_y1)]
    #
    #         # Устанавливаем обновленные данные в график
    #         data_line_y1.setData(t_data_y1, updated_values)
    #
    #     # Легенда: создаем, если ее нет
    #     if not hasattr(self, "legend"):
    #         self.legend = self.lock_in_plot.addLegend()
    #     else:
    #         self.legend.clear()  # Очищаем легенду
    #
    #     # Добавляем линии данных в легенду
    #     for key, line in self.data_lines.items():
    #         self.legend.addItem(line, key)
    #
    #     return data_dev, timestamp0

    def _setup_plots(self):
        # self.lock_in_plot.setTitle("title")
        self.lock_in_plot.addLegend()
        label_style = {'color': '#FFC300', 'font-size': '12px'}

        self.lock_in_plot.setLabel('left', 'Voltage', **label_style)
        self.lock_in_plot.setLabel('bottom', 'Time', **label_style)
        self.lock_in_plot.showGrid(x=True, y=True, alpha=0.3)

        self.hysteresis_plot.setLabel('left', 'Voltage', **label_style)
        self.hysteresis_plot.setLabel('bottom', 'Current', **label_style)
        self.hysteresis_plot.showGrid(x=True, y=True, alpha=0.3)

        self.label = pg.LabelItem(justify='right')
        self.graph_layout.addItem(self.label, row=0, col=0)
        # self.lock_in_plot.avgPen = pg.mkPen('#FFFFFF')
        # self.lock_in_plot.avgShadowPen = pg.mkPen('#8080DD', width=10)

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)
        self.lock_in_plot.addItem(self.v_line)
        self.lock_in_plot.addItem(self.h_line)

        self.lock_in_plot.scene().sigMouseMoved.connect(self.mouse_moved)
        self.lock_in_plot.sigRangeChanged.connect(self.handle_zoom)
        #
        # self.lock_in_plot.setXRange(-self.time_window, 0)
        # self.lock_in_plot.setLimits(xMin=-self.max_history, xMax=0)
        #
        # self.auto_scroll = True

        self.lock_in_plot.setDownsampling(auto=True, mode='peak')

    def mouse_moved(self, evt):
        pos = evt
        if self.lock_in_plot.sceneBoundingRect().contains(pos):
            mouse_point = self.lock_in_plot.vb.mapSceneToView(pos)
            x = mouse_point.x()
            y1 = mouse_point.y()
            y2 = mouse_point.y()

            self.label.setText(
                f"<span style='font-size: 12pt; color: orange'>"
                f"X: {x:.2f}, Y: {y1:.2f}, Y2: {y2:.2f}</span>"
            )

            self.v_line.setPos(x)
            self.h_line.setPos(y1)
            self.h_line.setPos(y2)

    def handle_zoom(self, window, view_range):
        x_start, x_end = view_range[0]
        self.auto_scroll = (x_end >= -0.1)

    def process_signal(self, data, signal_path):
        current_time = time.time()
        return {
            'time': np.array([current_time]),
            'values': np.array([data[signal_path]])
        }

# старый рабочий вариант
        # data_read = self.daq_module.read(flat=True)  # Считывание новых данных
        # returned_signal_paths = [
        #     signal_path.lower() for signal_path in data_read.keys()
        # ]
        #
        # for signal_path in self.signal_paths:
        #     if signal_path.lower() in returned_signal_paths:
        #         for index, signal_burst in enumerate(data_read[signal_path.lower()]):
        #             if timestamp0 is None or (isinstance(timestamp0, (float, int)) and np.isnan(timestamp0)):
        #                 timestamp0 = signal_burst["timestamp"][0, 0]  # Время старта
        #
        #             # Преобразование временной метки в секунды
        #             t = (signal_burst["timestamp"][0, :] - timestamp0) / self.clockbase
        #             value = signal_burst["value"][0, :]
        #
        #             # Сохранение данных
        #             data_dev[signal_path].extend(signal_burst["value"][0, :].tolist())  # Добавление точек на график
        #
        #             # Обновление графика
        #             if self.plot:
        #                 self.lock_in_gw.plot([], [], pen={'color': 'w', 'width': 1.5})
        #
        #
        #                 # Если график ещё не создан — инициализация
        #                 if not hasattr(self, f"data_line_{signal_path}"):
        #                     setattr(self, f"data_line_{signal_path}",
        #                             self.lock_in_gw.plot([], [] )) # pen={'color':'w', 'width':1.5}))
        #
        #
        #                 data_line = getattr(self, f"data_line_{signal_path}")
        #                 # data_line_x = getattr(self, f"data_line_{signal_path}")
        #                 # data_line_y = getattr(self, f"data_line_{signal_path}")
        #
        #                 # Добавляем новые точки (объединяем старые и новые)
        #
        #                 data_line.setData(
        #                     np.append(data_line.xData, t),
        #                     np.append(data_line.yData, value)
        #                 )
        #
        # # Обновляем заголовок графика с прогрессом
        # if self.plot:
        #     progress = self.daq_module.progress()[0]
        #     self.lock_in_gw.setTitle(f"Progress: {100 * progress:.2f}%")
        #
        # return data_dev, timestamp0

    # def read_data_update_plot(self, data_dev, timestamp0):
    #     """
    #     Read the acquired data out from the module and plot it. Raise an
    #     AssertionError if no data is returned.
    #     """
    #     data_read = self.daq_module.read(True)
    #     returned_signal_paths = [
    #         signal_path.lower() for signal_path in data_read.keys()
    #     ]
    #     progress = self.daq_module.progress()[0]
    #     # Loop over all the subscribed signals:
    #     for signal_path in self.signal_paths:
    #         if signal_path.lower() in returned_signal_paths:
    #             # Loop over all the bursts for the subscribed signal. More than
    #             # one burst may be returned at a time, in particular if we call
    #             # read() less frequently than the burst_duration.
    #             for index, signal_burst in enumerate(data_read[signal_path.lower()]):
    #                 if np.any(np.isnan(timestamp0)):
    #                     # Set our first timestamp to the first timestamp we obtain.
    #                     timestamp0 = signal_burst["timestamp"][0, 0]
    #                 # Convert from device ticks to time in seconds.
    #                 t = (signal_burst["timestamp"][0, :] - timestamp0) / self.clockbase
    #                 value = signal_burst["value"][0, :]
    #                 if self.plot:
    #                     self.data_line = self.lock_in_gw.plot(t, value)
    #                 num_samples = len(signal_burst["value"][0, :])
    #                 dt = (
    #                              signal_burst["timestamp"][0, -1]
    #                              - signal_burst["timestamp"][0, 0]
    #                      ) / self.clockbase
    #                 data_dev[signal_path].append(signal_burst)
    #
    #                 # print(
    #                 #     f"Read: {self.read_count}, progress: {100 * progress:.2f}%.",
    #                 #     f"Burst {index}: {signal_path} contains {num_samples} spanning {dt:.2f} s.",
    #                 # )
    #         else:
    #             # Note: If we read before the next burst has finished, there may be no new data.
    #             # No action required.
    #             pass
    #     #
    #     # Update the plot.
    #     if self.plot:
    #         # self.timer.setInterval(50)
    #         # self.timer.start()
    #         self.lock_in_gw.setTitle(f"Progress of data acquisition: {100 * progress:.2f}%.")
    #         # plot.pause(0.01)
    #     return data_dev, timestamp0

