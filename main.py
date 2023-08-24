import sys
import interface as i

from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    # i.MagnetCFU.init_port()
    # i.MagnetCFU.write_port("A007*IDN?")
    # i.MagnetCFU.receive_data()
    # i.MagnetCFU.close_port()

    window = i.MagnetCFU()
    window.show()

    app.exec()

