import os
# import magnetControl as mc

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


class WidgetsForApp(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)


        self.lbl_COM = QLabel("COM")
        lbl_I_start = QLabel("I start")
        lbl_I_stop = QLabel("I stop")
        lbl_Volt = QLabel("Volt")
        lbl_Amper = QLabel("Amper")
        lbl_Step = QLabel("Step")
        lbl_Resistance = QLabel("Resistance")
        lbl_Loops = QLabel("Loops")

        dsb_I_start = QDoubleSpinBox()
        dsb_I_stop = QDoubleSpinBox()
        dsb_Step = QDoubleSpinBox()
        sb_Loops = QSpinBox()
        le_IDN = QLineEdit()
        le_Resistance = QLineEdit()
        le_Volt = QLineEdit()
        le_Amper = QLineEdit()
        cb_COM = QComboBox()

            # dsb_I_start.valueChanged.connect(lambda: a)

        btn_IDN = QPushButton("&IDN")
        btn_Start = QPushButton("&Set Current")
        btn_Stop = QPushButton("&Stop")
        btn_Reset = QPushButton("Reset")
        btn_Start_Meas = QPushButton("&Start Measurment")
        btn_Open = QPushButton("&Open...")
        btn_Save = QPushButton("&Save")
