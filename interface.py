import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QFormLayout
)


class Magnet_CFU(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Magnet CFU")
        self.lbl_COM = QLabel("COM")
        self.btn_IDN = QPushButton("IDN")
        self.btn_Loops = QPushButton("Loops")
        self.btn_I_start = QPushButton("I start")
        self.btn_I_stop = QPushButton("I stop")
        self.btn_Volt = QPushButton("Volt")
        self.btn_Amper = QPushButton("Amper")
        self.btn_Step = QPushButton("Step")
        self.btn_Resistance = QPushButton("Resistance")
        self.btn_Start = QPushButton("Start")
        self.btn_Stop = QPushButton("Stop")
        self.btn_Reset = QPushButton("Reset")
        self.btn_Start_Meas = QPushButton("Start Measurment")
        self.btn_Open = QPushButton("Open...")

        outerLayout = QVBoxLayout()
        topLayout = QFormLayout()
        middleLayout = QVBoxLayout()
        layout_04 = QVBoxLayout()

        topLayout.addRow("IDN:", QLineEdit())
        middleLayout.addWidget(self.btn_Loops)
        middleLayout.addWidget(self.btn_I_start)
        middleLayout.addWidget(self.btn_I_stop)
        middleLayout.addWidget(self.btn_Amper)
        middleLayout.addWidget(self.btn_Step)
        middleLayout.addWidget(self.btn_Resistance)
        middleLayout.addWidget(self.btn_Start)
        middleLayout.addWidget(self.btn_Stop)
        middleLayout.addWidget(self.btn_Reset)
        middleLayout.addWidget(self.btn_Start_Meas)
        middleLayout.addWidget(self.btn_Open)

        # container = QWidget()
        # container.setLayout(layout_01)
        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        self.setLayout(outerLayout)

        # self.setCentralWidget(container)
        self.resize(800, 450)


app = QApplication(sys.argv)

window = Magnet_CFU()
window.show()

app.exec()
