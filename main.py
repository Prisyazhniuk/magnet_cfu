import sys
import interface as i

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

# app.setStyleSheet(
#     "QMainWindow  { background-color: black; }"
#     "QTabWidget::pane { border-top: 2px solid #0d192b; }"
#     "QTabBar::tab:selected, QTabBar::tab:hover { background: #0aa09e; color: black; }"
# )

# with open('styles.qss', 'r') as f:
#     style = f.read()
#     # Set the stylesheet of the application
#     app.setStyleSheet(style)

window = i.MagnetCFU()
window.show()

app.exec()

