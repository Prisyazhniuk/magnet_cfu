import sys
import interface as i

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

# colors app: #272829, #61677A, #D8D9DA, #FFF6E0

app.setStyleSheet(
    # "QMainWindow  { background-color: #F1F0E8; }
    "QTabWidget { font-family: sans-serif; font-size: 10pt; }"
    "QTabWidget::pane { border-top: 2px solid #272829; }"
    "QTabBar::tab:selected { background: #272829; color: #FFF6E0; }"
    "QTabBar::tab:hover { background: #61677A; color: #FFF6E0C; }"
    "QPushButton { padding: 6px; color: #27282; font-family: sans-serif; font-size: 10pt; }"
    "QLineEdit { margin: 0; font-size: 12pt; }"
    "QLabel { font-family: sans-serif; font-size: 10pt; }"
    "QComboBox { font-family: sans-serif; font-size: 10pt; }"
    "QSpinBox { font-family: sans-serif; font-size: 10pt; }"
    "QDoubleSpinBox { font-family: sans-serif; font-size: 10pt; }"
    "QGroupBox { font-size: 9pt; }"
    "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: #61677A; }"
)

# with open('styles.qss', 'r') as f:
#     style = f.read()
#     # Set the stylesheet of the application
#     app.setStyleSheet(style)

# i.MagnetCFU.init_port()
# i.MagnetCFU.write_port("A007*IDN?")
# i.MagnetCFU.receive_data()
# i.MagnetCFU.close_port()

window = i.MagnetCFU()
window.show()

app.exec()

