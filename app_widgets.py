from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QSizePolicy,
    QLabel,
    QLineEdit,
    QWidget,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox,
    QTextEdit,
    QVBoxLayout
)


class HexWindow(QMainWindow):
    def __init__(self, parent=None):
        super(HexWindow, self).__init__(parent)

        widgets = WidgetsForApp()
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

        self.lbl_COM = QLabel("COM")
        self.lbl_I_start = QLabel("I start")
        self.lbl_I_stop = QLabel("I stop")
        self.lbl_Volt = QLabel("Volt")
        self.lbl_Amper = QLabel("Amper")
        self.lbl_Step = QLabel("Step")
        self.lbl_Resistance = QLabel("Resistance")
        self.lbl_Loops = QLabel("Loops")

        self.dsb_I_start = QDoubleSpinBox()
        self.dsb_I_stop = QDoubleSpinBox()
        self.dsb_Step = QDoubleSpinBox()
        self.sb_Loops = QSpinBox()
        self.le_IDN = QLineEdit()
        self.le_Resistance = QLineEdit()
        self.le_Volt = QLineEdit()
        self.le_Amper = QLineEdit()
        self.cb_COM = QComboBox()

        self.btn_IDN = QPushButton("&IDN")
        self.btn_Start = QPushButton("&Set Current")
        self.btn_Stop = QPushButton("&Stop")
        self.btn_Reset = QPushButton("Reset")
        self.btn_Start_Meas = QPushButton("&Start Measurment")
        self.btn_Open = QPushButton("&Open...")
        self.btn_Save = QPushButton("&Save")

        # Config Tab
        self.btn_port_open = QPushButton("Open")
        self.btn_port_open.setCheckable(True)
        self.btn_open_serial_data = QPushButton("Open Serial data")

        self.cb_port_names = QComboBox()
        self.cb_baud_rates = QComboBox()
        self.cb_data_bits = QComboBox()
        self.cb_parity = QComboBox()
        self.cb_stop_bits = QComboBox()
        self.cb_flowControl = QComboBox()


        self.cb_port_names.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        self.cb_baud_rates.addItems([
            '110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800',
            '31250', '38400', '51200', '56000', '57600', '76800', '115200', '128000', '230400', '256000', '921600'
        ])
        self.cb_baud_rates.setCurrentText('115200')
        self.cb_data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.cb_data_bits.setCurrentText('8 bit')
        self.cb_parity.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])
        self.cb_stop_bits.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.cb_flowControl.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])

        # Group Box
        self.box_1 = QGroupBox("Info")
        self.box_2 = QGroupBox("Value")
        self.box_3 = QGroupBox("Control")

        # Data View parameters
        self.serial_data = QLineEdit()
        self.serial_data.setReadOnly(1)
        # self.serial_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set parameters
        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_I_start.setRange(-7.5, 7.5)
        self.dsb_I_stop.setRange(-7.5, 7.5)
        self.dsb_Step.setRange(0.01, 0.05)

        self.cb_COM.setFixedWidth(90)
        self.sb_Loops.setValue(1)

        self.btn_Start_Meas.setCheckable(1)
        self.btn_Reset.setCheckable(1)
        self.btn_Start.setCheckable(1)
        self.btn_IDN.setCheckable(1)

        self.le_IDN.setReadOnly(1)
        self.le_Volt.setReadOnly(1)
        self.le_Amper.setReadOnly(1)
        self.le_Resistance.setReadOnly(1)

        self.le_Amper.setFixedWidth(70)
        self.le_Volt.setFixedWidth(70)
        self.le_Amper.setPlaceholderText("0.0 A")
        self.le_Volt.setPlaceholderText("0.0 V")

        self.dsb_Step.setFixedWidth(60)
        self.dsb_I_start.setFixedWidth(60)
        self.dsb_I_stop.setFixedWidth(60)

        self.lbl_Resistance.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dsb_I_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_I_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dsb_I_stop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_I_stop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_Loops.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_Amper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_Volt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_Step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dsb_Step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_Loops.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.le_Amper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_COM.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.le_Volt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.le_IDN.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cb_COM.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])


# if __name__ == "__main__":
#     import sys
#     app = QApplication(sys.argv)
#     window = WidgetsForApp()
#     window.show()
#     sys.exit(app.exec())
