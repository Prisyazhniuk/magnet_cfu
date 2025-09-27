from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
                             QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
                             QPushButton, QCheckBox, QProgressBar)
from PyQt5.QtCore import pyqtSignal, QTimer
import numpy as np


class ControlTab(QWidget):
    """
    Вкладка управления магнитом и измерениями
    """

    # Сигналы
    start_measurement = pyqtSignal(dict)  # параметры измерения
    stop_measurement = pyqtSignal()
    clear_plots = pyqtSignal()

    pause_measurement = pyqtSignal()
    resume_measurement = pyqtSignal()

    def __init__(self, magnet_controller, lockin_controller, hysteresis_measurement, parent=None):
        super().__init__(parent)
        self.magnet_controller = magnet_controller
        self.lockin_controller = lockin_controller
        self.hysteresis_measurement = hysteresis_measurement
        self.is_measuring = False
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.update_measurement)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Инициализация интерфейса вкладки"""
        layout = QVBoxLayout(self)

        # Группа подключения
        connection_group = QGroupBox("Connection")
        connection_layout = QGridLayout(connection_group)

        self.port_combo = QComboBox()
        self.refresh_ports_btn = QPushButton("Refresh")
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setCheckable(True)

        # Добавляем кнопку IDN и поле для вывода
        self.btn_idn = QPushButton("IDN")
        self.le_idn = QLineEdit()
        self.le_idn.setReadOnly(True)

        connection_layout.addWidget(QLabel("Port:"), 0, 0)
        connection_layout.addWidget(self.port_combo, 0, 1)
        connection_layout.addWidget(self.refresh_ports_btn, 0, 2)
        connection_layout.addWidget(self.connect_btn, 1, 0, 1, 3)

        # Добавляем строку для IDN
        connection_layout.addWidget(self.btn_idn, 2, 0)
        connection_layout.addWidget(self.le_idn, 2, 1, 1, 2)

        # НОВАЯ ГРУППА: Управление током
        current_control_group = QGroupBox("Current Control")
        current_control_layout = QGridLayout(current_control_group)

        # Поле для установки конкретного значения тока
        self.target_current_spin = QDoubleSpinBox()
        self.target_current_spin.setRange(-7.5, 7.5)
        self.target_current_spin.setSingleStep(0.01)
        self.target_current_spin.setValue(0.0)
        self.target_current_spin.setDecimals(3)

        self.btn_set_current = QPushButton("Set Current")
        self.btn_reset_current = QPushButton("Reset to Zero")
        self.btn_reset_current.setStyleSheet("QPushButton { background-color: #ffcccc; }")

        current_control_layout.addWidget(QLabel("Target Current (A):"), 0, 0)
        current_control_layout.addWidget(self.target_current_spin, 0, 1)
        current_control_layout.addWidget(self.btn_set_current, 1, 0)
        current_control_layout.addWidget(self.btn_reset_current, 1, 1)

        # Группа параметров измерения
        measurement_group = QGroupBox("Measurement Parameters")
        measurement_layout = QGridLayout(measurement_group)

        self.start_current_spin = QDoubleSpinBox()
        self.start_current_spin.setRange(-7.5, 7.5)
        self.start_current_spin.setSingleStep(0.01)
        self.start_current_spin.setValue(0.0)
        self.start_current_spin.setDecimals(3)

        self.stop_current_spin = QDoubleSpinBox()
        self.stop_current_spin.setRange(-7.5, 7.5)
        self.stop_current_spin.setSingleStep(0.01)
        self.stop_current_spin.setValue(1.0)
        self.stop_current_spin.setDecimals(3)

        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.001, 0.1)
        self.step_spin.setSingleStep(0.001)
        self.step_spin.setValue(0.01)
        self.step_spin.setDecimals(3)

        self.loops_spin = QSpinBox()
        self.loops_spin.setRange(1, 100)
        self.loops_spin.setValue(1)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSuffix(" ms")

        measurement_layout.addWidget(QLabel("Start Current (A):"), 0, 0)
        measurement_layout.addWidget(self.start_current_spin, 0, 1)
        measurement_layout.addWidget(QLabel("Stop Current (A):"), 1, 0)
        measurement_layout.addWidget(self.stop_current_spin, 1, 1)
        measurement_layout.addWidget(QLabel("Step (A):"), 2, 0)
        measurement_layout.addWidget(self.step_spin, 2, 1)
        measurement_layout.addWidget(QLabel("Loops:"), 3, 0)
        measurement_layout.addWidget(self.loops_spin, 3, 1)
        measurement_layout.addWidget(QLabel("Interval:"), 4, 0)
        measurement_layout.addWidget(self.interval_spin, 4, 1)

        # Группа управления измерениями (убираем старую кнопку Set Current)
        control_group = QGroupBox("Measurement Control")
        control_layout = QGridLayout(control_group)

        self.start_btn = QPushButton("Start Measurement")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Размещаем кнопки в 2 строки
        control_layout.addWidget(self.start_btn, 0, 0)
        control_layout.addWidget(self.pause_btn, 0, 1)
        control_layout.addWidget(self.stop_btn, 1, 0, 1, 2)
        control_layout.addWidget(self.progress_bar, 2, 0, 1, 2)

        # Группа текущих значений
        values_group = QGroupBox("Current Values")
        values_layout = QGridLayout(values_group)

        self.voltage_label = QLabel("0.00 V")
        self.current_label = QLabel("0.00 A")
        self.resistance_label = QLabel("0.00 Ω")

        values_layout.addWidget(QLabel("Voltage:"), 0, 0)
        values_layout.addWidget(self.voltage_label, 0, 1)
        values_layout.addWidget(QLabel("Current:"), 1, 0)
        values_layout.addWidget(self.current_label, 1, 1)
        values_layout.addWidget(QLabel("Resistance:"), 2, 0)
        values_layout.addWidget(self.resistance_label, 2, 1)

        # Добавляем группы в layout
        layout.addWidget(connection_group)
        layout.addWidget(current_control_group)  # Новая группа
        layout.addWidget(measurement_group)
        layout.addWidget(control_group)
        layout.addWidget(values_group)
        layout.addStretch()

        # Обновляем список портов
        self.refresh_ports()

    def connect_signals(self):
        """Подключение сигналов"""
        self.refresh_ports_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.start_btn.clicked.connect(self.start_measurement_handler)
        self.stop_btn.clicked.connect(self.stop_measurement_handler)
        self.btn_idn.clicked.connect(self.on_btn_idn)

        # НОВЫЕ сигналы для управления током
        self.btn_set_current.clicked.connect(self.on_btn_set_current)
        self.btn_reset_current.clicked.connect(self.on_btn_reset_current)

        self.pause_btn.clicked.connect(self.pause_measurement_handler)

        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self.on_pause_toggled)

    def on_pause_toggled(self, checked):
        """Обработчик переключения кнопки пауза"""
        if checked:
            self.pause_btn.setText("Resume")
            self.pause_measurement.emit()
        else:
            self.pause_btn.setText("Pause")
            self.resume_measurement.emit()

    def pause_measurement_handler(self):
        """Обработчик кнопки пауза/возобновления"""
        # Логика уже реализована в on_pause_toggled через сигнал toggled
        pass

    def refresh_ports(self):
        """Обновление списка доступных портов"""
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = self.magnet_controller.get_available_ports()
        self.port_combo.addItems(ports)
        if current in ports:
            self.port_combo.setCurrentText(current)
        elif ports:
            self.port_combo.setCurrentIndex(0)

    def toggle_connection(self, checked):
        """Подключение/отключение от магнита"""
        print(f"Toggle connection called with checked={checked}")

        if checked:
            port = self.port_combo.currentText()
            print(f"Attempting to connect to port: {port}")

            if not port:
                self.connect_btn.setChecked(False)
                return

            try:
                if self.magnet_controller.connect(port):
                    self.connect_btn.setText("Disconnect")
                    print("Connection successful")
                else:
                    self.connect_btn.setChecked(False)
                    print("Connection failed")
            except Exception as e:
                print(f"Connection error: {e}")
                import traceback
                traceback.print_exc()
                self.connect_btn.setChecked(False)
        else:
            try:
                self.magnet_controller.disconnect()
                self.connect_btn.setText("Connect")
                print("Disconnected successfully")
            except Exception as e:
                print(f"Disconnection error: {e}")
                import traceback
                traceback.print_exc()

    def on_magnet_connection_changed(self, connected):
        """Обновление интерфейса при изменении подключения"""
        self.connect_btn.setChecked(connected)
        self.connect_btn.setText("Disconnect" if connected else "Connect")
        self.port_combo.setEnabled(not connected)
        self.refresh_ports_btn.setEnabled(not connected)

        # Включаем/отключаем кнопки управления током
        self.btn_set_current.setEnabled(connected)
        self.btn_reset_current.setEnabled(connected)
        self.btn_idn.setEnabled(connected)

    def on_btn_idn(self):
        """Обработчик кнопки IDN"""
        if not self.magnet_controller.is_connected:
            print("Not connected to magnet")
            return

        try:
            response = self.magnet_controller.send_command("*IDN?")
            if response:
                self.le_idn.setText(response)
                print(f"IDN response: {response}")
            else:
                self.le_idn.setText("No response")
                print("No response from IDN command")
        except Exception as e:
            print(f"IDN error: {e}")
            self.le_idn.setText(f"Error: {str(e)}")

    def on_btn_set_current(self):
        """Обработчик кнопки Set Current - устанавливает ток из target_current_spin"""
        if not self.magnet_controller.is_connected:
            print("Not connected to magnet")
            return

        try:
            current = self.target_current_spin.value()
            print(f"Setting current to: {current} A")

            success = self.magnet_controller.set_current(current)
            if success:
                print("Current set successfully")
                # Читаем текущие измерения после установки тока
                self.read_current_measurements()
            else:
                print("Failed to set current")
        except Exception as e:
            print(f"Set current error: {e}")

    def on_btn_reset_current(self):
        """Обработчик кнопки Reset to Zero"""
        if not self.magnet_controller.is_connected:
            print("Not connected to magnet")
            return

        try:
            print("Resetting current to zero...")
            # Сначала обновляем поле
            self.target_current_spin.setValue(0.0)
            # Затем устанавливаем ток
            success = self.magnet_controller.set_current(0.0)
            if success:
                print("Current reset to zero successfully")
                self.read_current_measurements()
            else:
                print("Failed to reset current")
        except Exception as e:
            print(f"Reset current error: {e}")

    def read_current_measurements(self):
        """Чтение текущих измерений и обновление интерфейса"""
        if not self.magnet_controller.is_connected:
            return

        try:
            measurements = self.magnet_controller.read_measurements()
            if measurements:
                voltage = measurements.get('voltage', 0)
                current = measurements.get('current', 0)
                resistance = voltage / current if current != 0 else 0

                self.voltage_label.setText(f"{voltage:.3f} V")
                self.current_label.setText(f"{current:.3f} A")
                self.resistance_label.setText(f"{resistance:.2f} Ω")
        except Exception as e:
            print(f"Read measurements error: {e}")

    def start_measurement_handler(self):
        """Обработчик запуска измерения"""
        if not self.magnet_controller.is_connected:
            return

        parameters = {
            'start_current': self.start_current_spin.value(),
            'stop_current': self.stop_current_spin.value(),
            'step': self.step_spin.value(),
            'loops': self.loops_spin.value(),
            'interval': self.interval_spin.value(),
            'settling_time': 1000
        }

        self.is_measuring = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.progress_bar.setVisible(True)

        self.start_measurement.emit(parameters)

    def stop_measurement_handler(self):
        """Обработчик остановки измерения"""
        self.is_measuring = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setChecked(False)
        self.pause_btn.setText("Pause")
        self.progress_bar.setVisible(False)

        self.stop_measurement.emit()

    def update_measurement(self):
        """Обновление прогресса измерения"""
        if self.is_measuring:
            # Обновляем прогресс-бар и читаем измерения
            self.read_current_measurements()

    def update_measurements(self, data):
        """Обновление текущих значений из внешнего источника"""
        voltage = data.get('voltage', 0)
        current = data.get('current', 0)
        resistance = voltage / current if current != 0 else 0

        self.voltage_label.setText(f"{voltage:.3f} V")
        self.current_label.setText(f"{current:.3f} A")
        self.resistance_label.setText(f"{resistance:.2f} Ω")

    def set_default_port(self, port):
        """Установка порта по умолчанию"""
        if port in [self.port_combo.itemText(i) for i in range(self.port_combo.count())]:
            self.port_combo.setCurrentText(port)
