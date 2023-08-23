import sys
import interface as i

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

# colors app: #272829, #61677A, #D8D9DA, #FFF6E0

app.setStyleSheet(
    # "QMainWindow  { background-color: black; }"
    "QTabWidget::pane { border-top: 2px solid #272829; }"
    "QTabBar::tab:selected { background: #272829; color: #FFF6E0; }"
    " QTabBar::tab:hover { background: #61677A; color: #FFF6E0C; }"
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

