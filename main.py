import sys
import interface as i

import zhinst.core

from zhinst.core import __version__ as zhinst_version
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

    # Worked script
    device_id = "dev4999"  # Device serial number available on its rear panel.
    interface = "1GbE"  # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.
    # interface = "USB" # For all instruments connected to the host computer via USB except MFLI/MFIA.
    # interface = "PCIe" # For MFLI/MFIA devices in case the Data Server runs on the device.

    server_host = "localhost"
    server_port = 8004
    api_level = 6  # Maximum API level supported for all instruments.

    # Create an API session to the Data Server.
    daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
    # Establish a connection between Data Server and Device.
    daq.connectDevice(device_id, interface)

    daq.setInt(f"/{device_id}/system/identify", 1)

    if daq.revision() == daq.getInt("/zi/about/revision"):
        print("LabOne and zhinst.core version match.")
    else:
        labone_version = daq.getString("/zi/about/version")
        labone_revision = daq.getInt("/zi/about/revision")
        print(
            f"zhinst.core version ({zhinst_version}) does not match",
            f"the LabOne version ({labone_version}.{str(labone_revision)[4:]})!",
         )

    app.exec()

