import sys
import interface as i
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    app = pg.mkQApp("Magnet CFU")

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = i.MagnetCFU()
    window.show()

    app.exec()

