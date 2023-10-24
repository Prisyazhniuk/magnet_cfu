
# import zhinst.core

# from zhinst.core import __version__ as zhinst_version

# Draw a graph
# self.timer.setInterval(50)
# self.timer.timeout.connect(self.update_plot_data)
# self.timer.start()
#
# self.x = list(range(100))  # 100 time points
# self.y = [randint(0, 100) for _ in range(100)]  # 100 data points
# pen = pg.mkPen(color=(255, 0, 0), width=15, style=Qt.DotLine)
# self.data_line = self.graph_widget.plot(self.x, self.y)
# self.graph_widget.setTitle("<span style=\"color:blue;font-size:20pt\">Hysteresis</span>")
# styles = {'color': 'r', 'font-size': '20px'}
# self.graph_widget.setLabel('left', 'Temperature (°C)', **styles)
# self.graph_widget.setLabel('bottom', 'Hour (H)', **styles)
# self.graph_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)
# self.graph_widget.showGrid(x=True, y=True)


# self.timer_mang.setInterval(self.sb_interval.value() / 4)
# self.timer_mang.timeout.connect(self.on_btn_idn)

# Data View parameters
# self.serial_data = QLineEdit()
# self.serial_data.setReadOnly(1)
# self.serial_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# magnet_dir = os.path.dirname(os.path.realpath(__file__))
# self.setWindowIcon(QIcon(magnet_dir + os.path.sep + 'icons\\01.png'))

# plt.addLegend()
# c1 = plt.plot([1, 3, 2, 4], pen='y', name='Yellow Plot')
# c2 = plt.plot([2, 1, 4, 3], pen='b', fillLevel=0, fillBrush=(255, 255, 255, 30), name='Blue Plot')
# c3 = plt.addLine(y=4, pen='y')

# self.btn_save.clicked.connect(self.on_clicked_btn_save)
# self.port.readyRead.connect(self.read_from_port)

# self.port.close()
# self.status_text.setText("Port closed")
# self.serialControlEnable(True)

# self.timer_mang.start()

# self.serial_control_enable(False) # flag on configs serial port
# self.port.isDataTerminalReady()
# self.port.readyRead.emit()

# def on_clicked_btn_save(self):
#     print()
#
# def update_plot_data(self):
#     self.x = self.x[1:]  # Remove the first y element.
#     self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
#
#     self.y = self.y[1:]  # Remove the first
#     self.y.append(randint(0, 100))  # Add a new random value.
#     self.data_line.setData(self.x, self.y)  # Update the data.


# server_host = 'localhost'
# # A session opened to LabOne Data Server
# session = Session(server_host)
# # A session opened to HF2 Data Server
# hf2_session = Session(server_host, hf2=True)
# device = session.connect_device("DEV4999")
# device.demods[0].rate.node_info

# # Worked script
# device_id = "dev4999"  # Device serial number available on its rear panel.
# interface = "1GbE"  # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.
# # interface = "USB" # For all instruments connected to the host computer via USB except MFLI/MFIA.
# # interface = "PCIe" # For MFLI/MFIA devices in case the Data Server runs on the device.
#
# server_host = "localhost"
# server_port = 8004
# api_level = 6  # Maximum API level supported for all instruments.
#
# # Create an API session to the Data Server.
# daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
# # Establish a connection between Data Server and Device.
# daq.connectDevice(device_id, interface)
#
# daq.setInt(f"/{device_id}/system/identify", 1)
#
# if daq.revision() == daq.getInt("/zi/about/revision"):
#     print("LabOne and zhinst.core version match.")
# else:
#     labone_version = daq.getString("/zi/about/version")
#     labone_revision = daq.getInt("/zi/about/revision")
#     print(
#         f"zhinst.core version ({zhinst_version}) does not match",
#         f"the LabOne version ({labone_version}.{str(labone_revision)[4:]})!",
#     )



# /* QWidget {*/
# /*   background-color: #000000;*/
# /*}*/
#
# /*QTabWidget::pane { *//* The tab widget frame */
# /*    border-top: 2px solid #0D192B;*/
# /*}*/
# /*QTabWidget::tab-bar {*/
# /*    left: 5px; *//* move to the right by 5px */
# /*}*/
# /* Style the tab using the tab sub-control. Note that*/
# /*    it reads QTabBar _not_ QTabWidget */
# /*QTabBar::tab {*/
# /*    background: #1B263B;*/
# /*    border-top-left-radius: 4px;*/
# /*    border-top-right-radius: 4px;*/
# /*    min-width: 8ex;*/
# /*    padding: 2px;*/
# /*    color: #E0E1DD;*/
# /*}*/
#
# /*QTabBar::tab:selected, QTabBar::tab:hover {*/
# /*    background: #0AA09E;*/
# /*    color: #000000;*/
#
# /*}*/
#
# /*QTabBar::tab:!selected {*/
# /*    margin-top: 2px; *//* make non-selected tabs look smaller */
# /*}*/
#
# /*QLineEdit {*/
# /*   background-color: #E0E1DD;*/
# /*   color: #415A77;*/
# /*   font-style: italic;*/
# /*   font-weight: bold;*/
# /*}*/
#
# /*QLabel {*/
# /*    background-color: #1B263B;*/
# /*    color: #E0E1DD;*/
# /*}*/
#
# /*QPushButton {*/
# /*   background-color: #778DA9;*/
# /*   color: #0D1B2A;*/
# /*   border-radius: 3px;*/
# /*   border-style: none;*/
# /*   height: 25px;*/
# /*}*/
#
# /*QPushButton:hover {*/
# /*   background-color: #415A77;*/
# /*   color: #E0E1DD;*/
# /*   border-radius: 3px;*/
# /*   border-style: none;*/
# /*   height: 25px;*/
# /*}*/
#
# /*QPushButton:focus {*/
# /*   background-color: #1B263B;*/
# /*   color: #E0E1DD;*/
# /*   border-radius: 3px;*/
# /*   border-style: none;*/
# /*   height: 25px;*/
# /*}*/
#
# /*QPushButton:pressed {*/
# /*    background-color: #415A77;*/
# /*    border-radius: 3px;*/
#
# /*}*/
#
# /*QComboBox {*/
# /*    background-color: #E0E1DD;*/
# /*    color: #1B263B;*/
# /*    border-radius: 3px;*/
# /*}*/
# /*QGroupBox {*/
# /*    background-color: #000000;*/
# /*    border: 2px solid #0D192B;*/
# /*    border-radius: 5px;*/
# /*    margin-top: 1ex; *//* leave space at the top for the title */
# /*    font-size: 10pt;*/
# /*}*/
#
# /*QGroupBox::title {*/
# /*    subcontrol-origin: margin;*/
# /*    subcontrol-position: top center; *//* position at the top center */
# /*    padding: 0 3px;*/
# /*    color: #778DA9;*/
# /*    font-style: italic;*/
# /*    font-weight: bold;*/
#
# /*}*/
# /*QGroupBox::indicator {*/
# /*    width: 13px;*/
# /*    height: 13px;*/
# /*}*/

