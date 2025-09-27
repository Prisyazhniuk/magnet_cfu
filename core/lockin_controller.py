import zhinst.toolkit
from zhinst.core import ziDAQServer, ziListEnum, ziDiscovery
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from config.settings import app_settings


class LockInController(QObject):
    """
    Контроллер для работы с Lock-in усилителем (MFLI)
    """

    # Сигналы
    connected = pyqtSignal(bool)
    data_ready = pyqtSignal(dict)  # данные с демодуляторов
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.daq = None
        self.device = None
        self.device_id = ""
        self.daq_module = None
        self.is_connected = False
        self.is_acquiring = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.data_buffer = {}  # буфер для хранения данных
        self.subscribed_paths = []
        self.clockbase = 1.0

    def connect_device(self, device_id: str = "dev4999", host: str = None, port: int = None,
                       api_level: int = None) -> bool:
        """
        Подключение к устройству через автодискавери или явные параметры
        """
        try:
            if host is None or port is None:
                # Используем автодискавери
                discovery = ziDiscovery()
                devices = discovery.getAll()

                if not devices:
                    self.error_occurred.emit("No Zurich Instruments devices found")
                    return False

                # Ищем устройство по ID или берем первое доступное
                device_info = None
                for dev_id, info in devices.items():
                    if device_id.lower() in dev_id.lower():
                        device_info = info
                        break

                if device_info is None:
                    device_info = list(devices.values())[0]

                host = device_info['serveraddress']
                port = device_info['serverport']
                device_id = device_info['deviceid']

            if api_level is None:
                api_level = app_settings.get("lockin.api_level", 6)

            self.daq = ziDAQServer(host, port, api_level)
            self.device_id = device_id
            self.device = self.daq.connectDevice(self.device_id)
            self.clockbase = float(self.daq.getInt(f'/{self.device_id}/clockbase'))

            self.is_connected = True
            self.connected.emit(True)
            self.status_update.emit(f"Connected to {device_id} at {host}:{port}")
            return True

        except Exception as e:
            self.error_occurred.emit(f"Connection error: {str(e)}")
            self.is_connected = False
            self.connected.emit(False)
            return False

    def disconnect_device(self):
        """Отключение от устройства"""
        if self.daq_module:
            self.stop_acquisition()
        if self.daq:
            try:
                self.daq.disconnectDevice(self.device_id)
            except:
                pass
            self.daq = None
        self.device = None
        self.is_connected = False
        self.connected.emit(False)
        self.status_update.emit("Disconnected")

    def setup_demodulator(self, demod_index: int = 0, parameters: Dict = None):
        """Настройка демодулятора"""
        if not self.is_connected:
            self.error_occurred.emit("Device not connected")
            return

        default_params = {
            "timeconstant": 0.1,
            "order": 4,
            "rate": 1674,
            "phaseshift": 90.0,
            "enable": 1
        }
        if parameters:
            default_params.update(parameters)

        base_path = f"/{self.device_id}/demods/{demod_index}/"
        for key, value in default_params.items():
            node = base_path + key
            try:
                if key in ["timeconstant", "phaseshift", "rate"]:
                    self.daq.setDouble(node, value)
                elif key in ["order", "enable"]:
                    self.daq.setInt(node, value)
            except Exception as e:
                self.error_occurred.emit(f"Error setting {key}: {str(e)}")

    def setup_signal_input(self, input_index: int = 0, parameters: Dict = None):
        """Настройка входа сигнала"""
        if not self.is_connected:
            self.error_occurred.emit("Device not connected")
            return

        default_params = {
            "range": 3.0,
            "scaling": 1.0,
            "ac": 1,
            "imp50": 1,
            "float": 0
        }
        if parameters:
            default_params.update(parameters)

        base_path = f"/{self.device_id}/sigins/{input_index}/"
        for key, value in default_params.items():
            node = base_path + key
            try:
                if key in ["range", "scaling"]:
                    self.daq.setDouble(node, value)
                elif key in ["ac", "imp50", "float"]:
                    self.daq.setInt(node, value)
            except Exception as e:
                self.error_occurred.emit(f"Error setting {key}: {str(e)}")

    def setup_signal_output(self, output_index: int = 0, parameters: Dict = None):
        """Настройка выхода сигнала"""
        if not self.is_connected:
            self.error_occurred.emit("Device not connected")
            return

        default_params = {
            "amplitudes/1": 0.1,  # амплитуда на выходе 1
            "enables/1": 1,  # включить выход 1
            "range": 1  # диапазон 1V
        }
        if parameters:
            default_params.update(parameters)

        base_path = f"/{self.device_id}/sigouts/{output_index}/"
        for key, value in default_params.items():
            node = base_path + key
            try:
                if key in ["amplitudes/1", "range"]:
                    self.daq.setDouble(node, value)
                elif key in ["enables/1"]:
                    self.daq.setInt(node, value)
            except Exception as e:
                self.error_occurred.emit(f"Error setting {key}: {str(e)}")

    def start_acquisition(self, signal_paths: List[str] = None):
        """Запуск сбора данных"""
        if not self.is_connected:
            self.error_occurred.emit("Device not connected")
            return

        if signal_paths is None:
            signal_paths = [f"/{self.device_id}/demods/0/sample.x",
                            f"/{self.device_id}/demods/0/sample.y"]

        try:
            # Настройка модуля сбора данных
            self.daq_module = self.daq.dataAcquisitionModule()
            self.daq_module.set("device", self.device_id)
            self.daq_module.set("type", 0)  # непрерывная запись
            self.daq_module.set("endless", 1)
            self.daq_module.set("grid/mode", 2)  # интерполяция
            self.daq_module.set("duration", 0.02)  # длительность одного блока
            self.daq_module.set("grid/cols", 1)  # количество точек
            self.daq_module.set("count", 0)  # бесконечный сбор

            # Подписка на сигналы
            for path in signal_paths:
                self.daq_module.subscribe(path)

            # Запуск
            self.daq_module.execute()
            self.is_acquiring = True
            self.subscribed_paths = signal_paths

            # Запуск таймера обновления данных
            self.timer.start(50)  # обновление каждые 50 мс
            self.status_update.emit("Acquisition started")

        except Exception as e:
            self.error_occurred.emit(f"Error starting acquisition: {str(e)}")

    def stop_acquisition(self):
        """Остановка сбора данных"""
        if self.daq_module:
            try:
                self.daq_module.finish()
                self.daq_module.clear()
            except:
                pass
            self.daq_module = None

        self.timer.stop()
        self.is_acquiring = False
        self.status_update.emit("Acquisition stopped")

    def update_data(self):
        """Обновление данных (вызывается по таймеру)"""
        if not self.is_acquiring or not self.daq_module:
            return

        try:
            # Чтение данных
            data_read = self.daq_module.read(flat=True)
            if not data_read:
                return

            # Обработка данных
            processed_data = {}
            for path in self.subscribed_paths:
                if path in data_read:
                    sample = data_read[path][0]
                    if sample["value"].size > 0:
                        value = sample["value"][0, 0]
                        timestamp = sample["timestamp"][0, 0]
                        processed_data[path] = {
                            "value": value,
                            "timestamp": timestamp,
                            "time_relative": (timestamp - self.clockbase) / self.clockbase
                        }

            # Отправка данных
            if processed_data:
                self.data_ready.emit(processed_data)

            # Перезапуск модуля если сбор завершен
            if self.daq_module.progress()[0] >= 1.0:
                self.daq_module.finish()
                self.daq_module.execute()

        except Exception as e:
            self.error_occurred.emit(f"Error reading data: {str(e)}")

    def get_device_info(self) -> Dict:
        """Получение информации об устройстве"""
        if not self.is_connected:
            return {}

        try:
            discovery = ziDiscovery()
            device_info = discovery.get(self.device_id)
            return {
                'device_type': device_info.get('devicetype', 'Unknown'),
                'device_id': device_info.get('deviceid', 'Unknown'),
                'server_address': device_info.get('serveraddress', 'Unknown'),
                'server_port': device_info.get('serverport', 'Unknown'),
                'server_version': device_info.get('serverversion', 'Unknown')
            }
        except:
            return {}