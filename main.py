import sys
import interface as i
#import modified_interface_v2 as i

from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = i.MagnetCFU()
    window.show()

    app.exec()

