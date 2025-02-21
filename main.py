import sys
import interface
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    app = pg.mkQApp()

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = interface.MagnetCFU()
    window.show()

    app.exec()
