from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QLineEdit,
    QWidget,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox,
)


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

            # dsb_I_start.valueChanged.connect(lambda: a)

        self.btn_IDN = QPushButton("&IDN")
        self.btn_Start = QPushButton("&Set Current")
        self.btn_Stop = QPushButton("&Stop")
        self.btn_Reset = QPushButton("Reset")
        self.btn_Start_Meas = QPushButton("&Start Measurment")
        self.btn_Open = QPushButton("&Open...")
        self.btn_Save = QPushButton("&Save")

        self.box_1 = QGroupBox("Info")
        self.box_2 = QGroupBox("Value")
        self.box_3 = QGroupBox("Control")

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

        self.le_Amper.setFixedWidth(55)
        self.le_Volt.setFixedWidth(55)

        self.dsb_Step.setFixedWidth(55)
        self.dsb_I_start.setFixedWidth(55)
        self.dsb_I_stop.setFixedWidth(55)

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

        # self.lbl_COM.setFont(QFont('Arial', 8))
        # self.lbl_Resistance.setFont(QFont('Arial', 8))

        self.cb_COM.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])

        self.btn_IDN.clicked.connect(self.on_clicked_IDN)

    def on_clicked_IDN(self):
        self.btn_IDN.setDisabled(True)
        self.btn_Stop.setEnabled(True)