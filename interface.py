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
    QFormLayout,
    QTabWidget,
    QCheckBox
)


class Magnet_CFU(QMainWindow):
    def __init__(self):
        super().__init__()

        tabs = QTabWidget()
        tabs.addTab(self.hysteresisTabUI(), "Hysteresis")
        tabs.addTab(self.pumpProbeTabUI(), "Pump-probe")

        self.setWindowTitle("Magnet CFU")
        lbl_COM = QLabel("COM")
        btn_IDN = QPushButton("IDN")
        btn_Loops = QPushButton("Loops")
        btn_I_start = QPushButton("I start")
        btn_I_stop = QPushButton("I stop")
        btn_Volt = QPushButton("Volt")
        btn_Amper = QPushButton("Amper")
        btn_Step = QPushButton("Step")
        btn_Resistance = QPushButton("Resistance")
        btn_Start = QPushButton("Start")
        btn_Stop = QPushButton("Stop")
        btn_Reset = QPushButton("Reset")
        btn_Start_Meas = QPushButton("Start Measurment")
        btn_Open = QPushButton("Open...")

        outerLayout = QVBoxLayout()
        topLayout = QVBoxLayout()
        middleLayout = QVBoxLayout()
        bottomLayout = QVBoxLayout()

        topLayout.addWidget(tabs)
        middleLayout.addWidget(btn_Loops)
        middleLayout.addWidget(btn_I_start)
        middleLayout.addWidget(btn_I_stop)
        middleLayout.addWidget(btn_Amper)
        middleLayout.addWidget(btn_Step)
        middleLayout.addWidget(btn_Resistance)
        middleLayout.addWidget(btn_Start)
        middleLayout.addWidget(btn_Stop)
        middleLayout.addWidget(btn_Reset)
        middleLayout.addWidget(btn_Start_Meas)
        middleLayout.addWidget(btn_Open)

        container = QWidget()
        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        outerLayout.addLayout(bottomLayout)
        container.setLayout(outerLayout)

        self.setCentralWidget(container)
        self.resize(800, 450)


    def hysteresisTabUI(self):
        hysteresisTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("General Option 1"))
        layout.addWidget(QCheckBox("General Option 2"))
        return hysteresisTab

    def pumpProbeTabUI(self):
        pumpProbeTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("Network Option 1"))
        layout.addWidget(QCheckBox("Network Option 2"))
        pumpProbeTab.setLayout(layout)
        return pumpProbeTab


app = QApplication(sys.argv)

window = Magnet_CFU()
window.show()

app.exec()
