import sys
import interface as i

from zhinst.toolkit import Session
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('styles.qss', 'r') as file:
        app.setStyleSheet(file.read())

    window = i.MagnetCFU()
    window.show()

    # server_host = 'localhost'
    # # A session opened to LabOne Data Server
    # session = Session(server_host)
    # # A session opened to HF2 Data Server
    # hf2_session = Session(server_host, hf2=True)
    # device = session.connect_device("DEV4999")
    # device.demods[0].rate.node_info

    app.exec()

