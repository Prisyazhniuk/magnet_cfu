import sys
# import magnetControl as mc

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
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QDoubleSpinBox
)


class Magnet_CFU(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Magnet CFU")
        container    = QWidget()
        tabs         = QTabWidget()
        outerLayout  = QVBoxLayout()
        topLayout    = QGridLayout()
        middleLayout = QGridLayout()
        bottomLayout = QGridLayout()

        tabs.addTab(self.hysteresisTabUI(), "Hysteresis")
        tabs.addTab(self.pumpProbeTabUI(),  "Pump-probe")
        topLayout.addWidget(tabs)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        outerLayout.addLayout(bottomLayout)
        container.setLayout(outerLayout)

        self.setCentralWidget(container)
        self.resize(1000, 800)

    def hysteresisTabUI(self):
        hysteresis_tab = QWidget()
        middle_layout  = QGridLayout()
        outer_layout   = QVBoxLayout()
        top_layout     = QGridLayout()
        bottom_layout  = QGridLayout()
        ml_layout      = QVBoxLayout()
        mc_layout      = QVBoxLayout()
        mr_layout      = QVBoxLayout()

        lbl_COM        = QLabel("COM")
        btn_IDN        = QPushButton("IDN")
        btn_Loops      = QPushButton("Loops")

        lbl_I_start    = QLabel("I start")
        lbl_I_stop     = QLabel("I stop")
        lbl_Volt       = QLabel("Volt")
        lbl_Amper      = QLabel("Amper")
        lbl_Step       = QLabel("Step")
        lbl_Resistance = QLabel("Resistance")

        dsb_I_start    = QDoubleSpinBox(self)
        dsb_I_stop     = QDoubleSpinBox(self)
        dsb_Volt       = QDoubleSpinBox(self)
        dsb_Amper      = QDoubleSpinBox(self)
        dsb_Step       = QDoubleSpinBox(self)
        dsb_Resistance = QDoubleSpinBox(self)
        # dsb_I_start.valueChanged.connect(lambda: a)

        btn_Start      = QPushButton("Start")
        btn_Stop       = QPushButton("Stop")
        btn_Reset      = QPushButton("Reset")
        btn_Start_Meas = QPushButton("Start Measurment")
        btn_Open       = QPushButton("Open...")
        btn_Save       = QPushButton("Save")

        top_layout.addWidget(lbl_COM,           0, 0)
        top_layout.addWidget(btn_IDN,           0, 1)
        top_layout.addWidget(btn_Loops,         1, 0)

        middle_layout.addWidget(lbl_I_start,    0, 0)
        middle_layout.addWidget(lbl_I_stop,     2, 0)
        middle_layout.addWidget(lbl_Volt,       2, 2)
        middle_layout.addWidget(lbl_Amper,      0, 2)
        middle_layout.addWidget(lbl_Step,       0, 1)
        middle_layout.addWidget(lbl_Resistance, 2, 1)

        middle_layout.addWidget(dsb_I_start,    1, 0)
        middle_layout.addWidget(dsb_I_stop,     3, 0)
        middle_layout.addWidget(dsb_Amper,      3, 2)
        middle_layout.addWidget(dsb_Volt,       1, 2)
        middle_layout.addWidget(dsb_Step,       1, 1)
        middle_layout.addWidget(dsb_Resistance, 3, 1)

        bottom_layout.addWidget(btn_Start,      0, 0)
        bottom_layout.addWidget(btn_Stop,       0, 1)
        bottom_layout.addWidget(btn_Reset,      1, 0)
        bottom_layout.addWidget(btn_Start_Meas, 1, 1)
        bottom_layout.addWidget(btn_Open,       2, 0)
        bottom_layout.addWidget(btn_Save,       2, 1)

        dsb_I_start.setRange(-7.5, 7.5)
        dsb_I_stop.setRange(-7.5, 7.5)
        dsb_I_start.setRange(-7.5, 7.5)
        dsb_I_stop.setRange(-7.5, 7.5)
        dsb_Step.setRange(0.01, 0.05)

        outer_layout.addLayout(top_layout)
        outer_layout.addLayout(middle_layout)
        outer_layout.addLayout(bottom_layout)

        hysteresis_tab.setLayout(outer_layout)
        return hysteresis_tab

    def pumpProbeTabUI(self):
        pumpProbeTab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("Network Option 1"))
        layout.addWidget(QCheckBox("Network Option 2"))
        pumpProbeTab.setLayout(layout)
        return pumpProbeTab


    # def save_data(self):
    #     file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Data Files (*.dat)')
    #
    #     if file_name:
    #         with open(file_name, 'w') as f:
    #             f.write(self.data_file.toPlainText())

app = QApplication(sys.argv)

window = Magnet_CFU()
window.show()

app.exec()
