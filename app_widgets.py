import sys
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QLCDNumber,
    QSizePolicy,
    QFormLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox,
    QTextEdit,
    QVBoxLayout,
    QGraphicsWidget
)


class CustomDoubleSpinbox(QDoubleSpinBox):
    def validate(self, text: str, pos: int) -> object:
        text = text.replace(".", ",")
        return QDoubleSpinBox.validate(self, text, pos)

    def valueFromText(self, text: str) -> float:
        text = text.replace(",", ".")
        return float(text)


class newWindow(QMainWindow):
    def __init__(self, parent=None):
        super(newWindow, self).__init__(parent)

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


class WidgetsForApp(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.hysteresis = QWidget()

        self.hysteresis.setFixedSize(500, 300)

        # self.plotWidget = pg.PlotWidget(self)
        # self.plotWidget.plot([1, 2, 3, 4])
        # self.plotWidget.scene().sigMouseClicked.connect(self.onMouseClicked)
        # plt.addLegend()
        # self.c2 = plt.plot([2, 1, 4, 3], pen='b', fillLevel=0, fillBrush=(255, 255, 255, 30), name='Blue Plot')

        self.lbl_COM = QLabel("COM")
        self.lbl_I_start = QLabel("I start")
        self.lbl_I_stop = QLabel("I stop")
        self.lbl_volt = QLabel("Volt")
        self.lbl_volt.setFixedSize(45, 40)
        self.lbl_amper = QLabel("Amper")
        self.lbl_amper.setFixedSize(45, 40)
        self.lbl_step = QLabel("Step")
        self.lbl_resistance = QLabel("Resistance")
        self.lbl_loops = QLabel("Loops")

        self.dsb_I_start = QDoubleSpinBox()
        self.dsb_I_start.setSuffix(" A")
        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_start.setFixedSize(70, 35)
        self.dsb_I_stop = QDoubleSpinBox()
        self.dsb_I_stop.setSuffix(" A")
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_I_stop.setFixedSize(70, 35)
        self.dsb_step = QDoubleSpinBox()
        self.dsb_step.setSuffix(" A")
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
        self.le_resistance.setFixedSize(120, 35)
        self.le_volt = QLineEdit()
        self.le_volt.setDisabled(True)
        self.le_volt.setPlaceholderText("0.0 V")
        self.le_volt.setFixedSize(70, 35)
        self.le_amper = QLineEdit()
        self.le_amper.setDisabled(True)
        self.le_amper.setPlaceholderText("0.0 A")
        self.le_amper.setFixedSize(70, 35)
        self.cb_COM = QComboBox()
        self.cb_COM.setFixedWidth(90)

        self.btn_IDN = QPushButton("&IDN")
        self.btn_IDN.setCheckable(0)
        self.btn_IDN.setFixedWidth(70)
        self.btn_start = QPushButton("&Set Current")
        self.btn_start.setCheckable(1)
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

        # Connect all serial port to comboBox "COM in Hysteresis tab"
        self.cb_COM.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        if self.cb_COM.count() == 0:
            self.cb_COM.addItem("no ports")


# if __name__ == "__main__":
#     import sys
#     app = QApplication(sys.argv)
#     window = WidgetsForApp()
#     window.show()
#     sys.exit(app.exec())
