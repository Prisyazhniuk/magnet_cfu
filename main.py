import sys
<<<<<<< HEAD
import interface as i
#import modified_interface_v2 as i

=======
import interface
import pyqtgraph as pg
>>>>>>> 4020c5db9c89cec9eb751397274fc0b136c30499
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    app = pg.mkQApp()

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = interface.MagnetCFU()
    window.show()

    app.exec()
