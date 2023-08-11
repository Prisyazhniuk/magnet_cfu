import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QWidget
)


class Magnet_CFU(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Magnet CFU")
        self.btn_COM = QPushButton("COM")
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

        layout = QVBoxLayout()
        layout.addWidget(self.btn_COM)
        layout.addWidget(self.btn_IDN)
        layout.addWidget(self.btn_Loops)
        layout.addWidget(self.btn_I_start)
        layout.addWidget(self.btn_I_stop)
        layout.addWidget(self.btn_Amper)
        layout.addWidget(self.btn_Step)
        layout.addWidget(self.btn_Resistance)
        layout.addWidget(self.btn_Start)
        layout.addWidget(self.btn_Stop)
        layout.addWidget(self.btn_Reset)
        layout.addWidget(self.btn_Start_Meas)
        layout.addWidget(self.btn_Open)


        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


app = QApplication(sys.argv)

window = Magnet_CFU()
window.show()

app.exec()