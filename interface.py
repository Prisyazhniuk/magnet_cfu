import sys
import os
# import magnetControl as mc

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
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
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox
)


class Magnet_CFU(QMainWindow):
    def __init__(self):
        super().__init__()

        magnet_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))
        self.setWindowTitle("Magnet CFU")

        container    = QWidget()
        tabs         = QTabWidget()
        outerLayout  = QVBoxLayout()
        topLayout    = QGridLayout()
        middleLayout = QGridLayout()
        bottomLayout = QGridLayout()

        tabs.addTab(self.hysteresisTabUI(), "&Hysteresis")
        tabs.addTab(self.ConfigureTabUI(),  "&Configure")
        topLayout.addWidget(tabs)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(middleLayout)
        outerLayout.addLayout(bottomLayout)
        container.setLayout(outerLayout)

        self.setCentralWidget(container)
        self.resize(300, 500)

    def hysteresisTabUI(self):
        hysteresis_tab = QWidget()
        outer_layout   = QVBoxLayout()
        top_layout     = QGridLayout()
        middle_layout  = QGridLayout()
        bottom_layout  = QGridLayout()
        ml_layout      = QVBoxLayout()
        mc_layout      = QVBoxLayout()
        mr_layout      = QVBoxLayout()

        lbl_COM        = QLabel("COM")
        lbl_I_start    = QLabel("I start")
        lbl_I_stop     = QLabel("I stop")
        lbl_Volt       = QLabel("Volt")
        lbl_Amper      = QLabel("Amper")
        lbl_Step       = QLabel("Step")
        lbl_Resistance = QLabel("Resistance")
        lbl_Loops      = QLabel("Loops")

        dsb_I_start    = QDoubleSpinBox(self)
        dsb_I_stop     = QDoubleSpinBox(self)
        dsb_Step       = QDoubleSpinBox(self)
        sb_Loops       = QSpinBox(self)
        le_IDN         = QLineEdit()
        le_Resistance  = QLineEdit()
        le_Volt        = QLineEdit()
        le_Amper       = QLineEdit()
        cb_COM         = QComboBox()
        # dsb_I_start.valueChanged.connect(lambda: a)

        btn_IDN        = QPushButton("&IDN")
        btn_Start      = QPushButton("&Set Current")
        btn_Stop       = QPushButton("&Stop")
        btn_Reset      = QPushButton("Reset")
        btn_Start_Meas = QPushButton("&Start Measurment")
        btn_Open       = QPushButton("&Open...")
        btn_Save       = QPushButton("&Save")

        top_layout.addWidget(lbl_COM,           0, 0)
        top_layout.addWidget(cb_COM,            0, 1)
        top_layout.addWidget(btn_IDN,           1, 0)
        top_layout.addWidget(lbl_Resistance,    2, 0)
        top_layout.addWidget(le_IDN,            1, 1)
        top_layout.addWidget(le_Resistance,     2, 1)

        middle_layout.addWidget(lbl_I_start,    0, 0)
        middle_layout.addWidget(lbl_I_stop,     2, 0)
        middle_layout.addWidget(lbl_Volt,       2, 2)
        middle_layout.addWidget(lbl_Amper,      0, 2)
        middle_layout.addWidget(lbl_Step,       0, 1)
        middle_layout.addWidget(lbl_Loops,      2, 1)

        middle_layout.addWidget(dsb_I_start,    1, 0)
        middle_layout.addWidget(dsb_I_stop,     3, 0)
        middle_layout.addWidget(dsb_Step,       1, 1)
        middle_layout.addWidget(sb_Loops,       3, 1)
        middle_layout.addWidget(le_Amper,       3, 2)
        middle_layout.addWidget(le_Volt,        1, 2)

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
        cb_COM.setFixedWidth(50)
        sb_Loops.setValue(1)

        lbl_Resistance.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_I_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_I_stop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_Loops.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_Amper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_Volt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_Step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_COM.setAlignment(Qt.AlignmentFlag.AlignCenter)

        box_1 = QGroupBox("Info")
        box_2 = QGroupBox("Value")
        box_3 = QGroupBox("Control")

        box_1.setLayout(top_layout)
        box_2.setLayout(middle_layout)
        box_3.setLayout(bottom_layout)

        outer_layout.addLayout(top_layout)
        outer_layout.addLayout(middle_layout)
        outer_layout.addWidget(box_1)
        outer_layout.addWidget(box_2)
        outer_layout.addWidget(box_3)

        hysteresis_tab.setLayout(outer_layout)
        return hysteresis_tab

    def ConfigureTabUI(self):
        configure_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QCheckBox("Network Option 1"))
        layout.addWidget(QCheckBox("Network Option 2"))
        configure_tab.setLayout(layout)
        return configure_tab


    # def save_data(self):
    #     file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Data Files (*.dat)')
    #
    #     if file_name:
    #         with open(file_name, 'w') as f:
    #             f.write(self.data_file.toPlainText())

app = QApplication(sys.argv)

app.setStyleSheet(
    "QMainWindow { background-color: black;}"
    "QPushButton {font: 12px Roboto Mono;}"
)


window = Magnet_CFU()
window.show()

app.exec()
