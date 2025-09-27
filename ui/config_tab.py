from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QGridLayout,
                             QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit, QDoubleSpinBox)
from PyQt5.QtCore import pyqtSlot
from config.settings import app_settings


class ConfigTab(QWidget):
    """
    Вкладка конфигурации параметров приложения
    """

    def __init__(self, magnet_controller, parent=None):
        super().__init__(parent)
        self.magnet_controller = magnet_controller
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Инициализация интерфейса вкладки"""
        layout = QVBoxLayout(self)

        # Группа настроек последовательного порта
        serial_group = QGroupBox("Serial Port Settings")
        serial_layout = QGridLayout(serial_group)

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['9600', '19200', '38400', '57600', '115200'])

        self.databits_combo = QComboBox()
        self.databits_combo.addItems(['5', '6', '7', '8'])

        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'])

        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])

        self.flowcontrol_combo = QComboBox()
        self.flowcontrol_combo.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])

        serial_layout.addWidget(QLabel("Baud Rate:"), 0, 0)
        serial_layout.addWidget(self.baudrate_combo, 0, 1)
        serial_layout.addWidget(QLabel("Data Bits:"), 1, 0)
        serial_layout.addWidget(self.databits_combo, 1, 1)
        serial_layout.addWidget(QLabel("Parity:"), 2, 0)
        serial_layout.addWidget(self.parity_combo, 2, 1)
        serial_layout.addWidget(QLabel("Stop Bits:"), 3, 0)
        serial_layout.addWidget(self.stopbits_combo, 3, 1)
        serial_layout.addWidget(QLabel("Flow Control:"), 4, 0)
        serial_layout.addWidget(self.flowcontrol_combo, 4, 1)

        # Группа настроек Lock-in
        lockin_group = QGroupBox("Lock-in Settings")
        lockin_layout = QGridLayout(lockin_group)

        self.device_id_edit = QLineEdit()
        self.host_edit = QLineEdit()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)

        lockin_layout.addWidget(QLabel("Device ID:"), 0, 0)
        lockin_layout.addWidget(self.device_id_edit, 0, 1)
        lockin_layout.addWidget(QLabel("Host:"), 1, 0)
        lockin_layout.addWidget(self.host_edit, 1, 1)
        lockin_layout.addWidget(QLabel("Port:"), 2, 0)
        lockin_layout.addWidget(self.port_spin, 2, 1)

        # Группа настроек измерения
        measurement_group = QGroupBox("Measurement Settings")
        measurement_layout = QGridLayout(measurement_group)

        self.default_time_window_spin = QDoubleSpinBox()
        self.default_time_window_spin.setRange(1, 3600)
        self.default_time_window_spin.setSuffix(" s")

        self.auto_save_checkbox = QCheckBox("Auto-save data")

        measurement_layout.addWidget(QLabel("Default Time Window:"), 0, 0)
        measurement_layout.addWidget(self.default_time_window_spin, 0, 1)
        measurement_layout.addWidget(self.auto_save_checkbox, 1, 0, 1, 2)

        layout.addWidget(serial_group)
        layout.addWidget(lockin_group)
        layout.addWidget(measurement_group)
        layout.addStretch()

        # Подключаем сигналы изменений
        self.baudrate_combo.currentTextChanged.connect(self.save_settings)
        self.databits_combo.currentTextChanged.connect(self.save_settings)
        self.parity_combo.currentTextChanged.connect(self.save_settings)
        self.stopbits_combo.currentTextChanged.connect(self.save_settings)
        self.flowcontrol_combo.currentTextChanged.connect(self.save_settings)
        self.device_id_edit.textChanged.connect(self.save_settings)
        self.host_edit.textChanged.connect(self.save_settings)
        self.port_spin.valueChanged.connect(self.save_settings)
        self.default_time_window_spin.valueChanged.connect(self.save_settings)
        self.auto_save_checkbox.stateChanged.connect(self.save_settings)

    def load_settings(self):
        """Загрузка настроек из конфигурации"""
        # Настройки последовательного порта
        self.baudrate_combo.setCurrentText(
            str(app_settings.get("serial.baud_rate", 115200)))
        self.databits_combo.setCurrentText(
            str(app_settings.get("serial.data_bits", 8)))
        self.parity_combo.setCurrentText(
            app_settings.get("serial.parity", "No Parity"))
        self.stopbits_combo.setCurrentText(
            app_settings.get("serial.stop_bits", "One Stop"))
        self.flowcontrol_combo.setCurrentText(
            app_settings.get("serial.flow_control", "No Flow Control"))

        # Настройки Lock-in
        self.device_id_edit.setText(
            app_settings.get("lockin.device_id", "dev4999"))
        self.host_edit.setText(
            app_settings.get("lockin.host", "localhost"))
        self.port_spin.setValue(
            app_settings.get("lockin.port", 8004))

        # Настройки измерения
        self.default_time_window_spin.setValue(
            app_settings.get("measurement.default_time_window", 10))
        self.auto_save_checkbox.setChecked(
            app_settings.get("measurement.auto_save", True))

    def save_settings(self):
        """Сохранение настроек в конфигурацию"""
        # Настройки последовательного порта
        app_settings.set("serial.baud_rate", int(self.baudrate_combo.currentText()))
        app_settings.set("serial.data_bits", int(self.databits_combo.currentText()))
        app_settings.set("serial.parity", self.parity_combo.currentText())
        app_settings.set("serial.stop_bits", self.stopbits_combo.currentText())
        app_settings.set("serial.flow_control", self.flowcontrol_combo.currentText())

        # Настройки Lock-in
        app_settings.set("lockin.device_id", self.device_id_edit.text())
        app_settings.set("lockin.host", self.host_edit.text())
        app_settings.set("lockin.port", self.port_spin.value())

        # Настройки измерения
        app_settings.set("measurement.default_time_window", self.default_time_window_spin.value())
        app_settings.set("measurement.auto_save", self.auto_save_checkbox.isChecked())