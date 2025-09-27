from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QDoubleSpinBox, QSpinBox)
from PyQt5.QtCore import pyqtSlot
from config.settings import app_settings


class LockInTab(QWidget):
    """
    Вкладка управления Lock-in усилителем
    """

    def __init__(self, lockin_controller, parent=None):
        super().__init__(parent)
        self.lockin_controller = lockin_controller
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Инициализация интерфейса вкладки"""
        layout = QVBoxLayout(self)

        # Группа подключения
        connection_group = QGroupBox("Connection")
        connection_layout = QGridLayout(connection_group)

        self.device_id_edit = QLineEdit()
        self.host_edit = QLineEdit()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setCheckable(True)
        self.status_label = QLabel("Disconnected")

        connection_layout.addWidget(QLabel("Device ID:"), 0, 0)
        connection_layout.addWidget(self.device_id_edit, 0, 1)
        connection_layout.addWidget(QLabel("Host:"), 1, 0)
        connection_layout.addWidget(self.host_edit, 1, 1)
        connection_layout.addWidget(QLabel("Port:"), 2, 0)
        connection_layout.addWidget(self.port_spin, 2, 1)
        connection_layout.addWidget(self.connect_btn, 3, 0, 1, 2)
        connection_layout.addWidget(self.status_label, 4, 0, 1, 2)

        # Группа демодулятора
        demodulator_group = QGroupBox("Demodulator")
        demodulator_layout = QGridLayout(demodulator_group)

        self.frequency_edit = QLineEdit()
        self.frequency_edit.setReadOnly(True)
        self.time_constant_spin = QDoubleSpinBox()
        self.time_constant_spin.setRange(0.001, 10)
        self.time_constant_spin.setDecimals(3)
        self.time_constant_spin.setValue(0.1)

        self.phase_spin = QDoubleSpinBox()
        self.phase_spin.setRange(-180, 180)
        self.phase_spin.setValue(90)

        self.order_combo = QComboBox()
        self.order_combo.addItems([str(i) for i in range(1, 9)])
        self.order_combo.setCurrentIndex(3)  # 4th order

        self.auto_phase_btn = QPushButton("Auto Phase")

        demodulator_layout.addWidget(QLabel("Frequency (Hz):"), 0, 0)
        demodulator_layout.addWidget(self.frequency_edit, 0, 1)
        demodulator_layout.addWidget(QLabel("Time Constant (s):"), 1, 0)
        demodulator_layout.addWidget(self.time_constant_spin, 1, 1)
        demodulator_layout.addWidget(QLabel("Phase (deg):"), 2, 0)
        demodulator_layout.addWidget(self.phase_spin, 2, 1)
        demodulator_layout.addWidget(QLabel("Order:"), 3, 0)
        demodulator_layout.addWidget(self.order_combo, 3, 1)
        demodulator_layout.addWidget(self.auto_phase_btn, 4, 0, 1, 2)

        # Группа входа сигнала
        input_group = QGroupBox("Signal Input")
        input_layout = QGridLayout(input_group)

        self.input_range_spin = QDoubleSpinBox()
        self.input_range_spin.setRange(0.001, 10)
        self.input_range_spin.setValue(3.0)

        self.scaling_spin = QDoubleSpinBox()
        self.scaling_spin.setRange(0.001, 1000)
        self.scaling_spin.setValue(1.0)

        self.ac_coupling_check = QCheckBox("AC Coupling")
        self.ac_coupling_check.setChecked(True)

        self.imp50_check = QCheckBox("50 Ohm Impedance")
        self.imp50_check.setChecked(True)

        input_layout.addWidget(QLabel("Range (V):"), 0, 0)
        input_layout.addWidget(self.input_range_spin, 0, 1)
        input_layout.addWidget(QLabel("Scaling:"), 1, 0)
        input_layout.addWidget(self.scaling_spin, 1, 1)
        input_layout.addWidget(self.ac_coupling_check, 2, 0)
        input_layout.addWidget(self.imp50_check, 2, 1)

        layout.addWidget(connection_group)
        layout.addWidget(demodulator_group)
        layout.addWidget(input_group)
        layout.addStretch()

        # Загружаем настройки
        self.load_settings()

    def connect_signals(self):
        """Подключение сигналов"""
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.auto_phase_btn.clicked.connect(self.auto_phase)

        # Подключаем сигналы изменений параметров
        self.time_constant_spin.valueChanged.connect(self.update_demodulator)
        self.phase_spin.valueChanged.connect(self.update_demodulator)
        self.order_combo.currentTextChanged.connect(self.update_demodulator)
        self.input_range_spin.valueChanged.connect(self.update_input)
        self.scaling_spin.valueChanged.connect(self.update_input)
        self.ac_coupling_check.stateChanged.connect(self.update_input)
        self.imp50_check.stateChanged.connect(self.update_input)

    def load_settings(self):
        """Загрузка настроек"""
        self.device_id_edit.setText(app_settings.get("lockin.device_id", "dev4999"))
        self.host_edit.setText(app_settings.get("lockin.host", "localhost"))
        self.port_spin.setValue(app_settings.get("lockin.port", 8004))

    def toggle_connection(self, checked):
        """Подключение/отключение Lock-in"""
        if checked:
            device_id = self.device_id_edit.text()
            host = self.host_edit.text()
            port = self.port_spin.value()

            if self.lockin_controller.connect_device(device_id, host, port):
                self.connect_btn.setText("Disconnect")
                self.status_label.setText("Connected")
                # Применяем текущие настройки после подключения
                self.apply_all_settings()
            else:
                self.connect_btn.setChecked(False)
        else:
            self.lockin_controller.disconnect_device()
            self.connect_btn.setText("Connect")
            self.status_label.setText("Disconnected")

    def on_lockin_connection_changed(self, connected):
        """Обновление интерфейса при изменении подключения"""
        self.connect_btn.setChecked(connected)
        self.connect_btn.setText("Disconnect" if connected else "Connect")
        self.status_label.setText("Connected" if connected else "Disconnected")

        # Блокируем редактирование параметров при отключении
        self.time_constant_spin.setEnabled(connected)
        self.phase_spin.setEnabled(connected)
        self.order_combo.setEnabled(connected)
        self.input_range_spin.setEnabled(connected)
        self.scaling_spin.setEnabled(connected)
        self.ac_coupling_check.setEnabled(connected)
        self.imp50_check.setEnabled(connected)
        self.auto_phase_btn.setEnabled(connected)

    def auto_phase(self):
        """Автоматическая настройка фазы"""
        if self.lockin_controller.is_connected:
            # TODO: реализовать авто-фазу
            pass

    def update_demodulator(self):
        """Обновление параметров демодулятора"""
        if not self.lockin_controller.is_connected:
            return

        params = {
            'timeconstant': self.time_constant_spin.value(),
            'phaseshift': self.phase_spin.value(),
            'order': int(self.order_combo.currentText())
        }
        self.lockin_controller.setup_demodulator(0, params)

    def update_input(self):
        """Обновление параметров входа"""
        if not self.lockin_controller.is_connected:
            return

        params = {
            'range': self.input_range_spin.value(),
            'scaling': self.scaling_spin.value(),
            'ac': 1 if self.ac_coupling_check.isChecked() else 0,
            'imp50': 1 if self.imp50_check.isChecked() else 0
        }
        self.lockin_controller.setup_signal_input(0, params)

    def apply_all_settings(self):
        """Применение всех текущих настроек"""
        self.update_demodulator()
        self.update_input()
