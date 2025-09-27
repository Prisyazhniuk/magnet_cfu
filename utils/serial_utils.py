import serial
import serial.tools.list_ports
from contextlib import contextmanager
from typing import List, Optional, Generator
from PyQt5.QtCore import QObject, pyqtSignal
from config.settings import app_settings


def decimal_range(start, stop, increment):
    """Генератор диапазона с плавающей точкой"""
    while start < stop:
        yield start
        start += increment


def rev_decimal_range(start, stop, increment):
    """Генератор обратного диапазона с плавающей точкой"""
    while start > stop:
        yield start
        start -= increment


class SerialManager(QObject):
    """Менеджер для работы с последовательным портом"""

    # Сигналы
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_port = None
        self.is_connected = False

    def get_available_ports(self) -> List[str]:
        """Возвращает список доступных COM-портов"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect_to_port(self, port: str, baudrate: int = None) -> bool:
        """Подключается к указанному порту"""
        if baudrate is None:
            baudrate = app_settings.get("serial.baud_rate", 115200)

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=app_settings.get("serial.data_bits", 8),
                parity=app_settings.get("serial.parity", 'N'),
                stopbits=app_settings.get("serial.stop_bits", 1),
                timeout=app_settings.get("serial.timeout", 1)
            )
            self.is_connected = True
            self.connected.emit()
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"Ошибка подключения: {str(e)}")
            return False

    def disconnect(self):
        """Отключается от порта"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.disconnected.emit()

    def send_command(self, command: str, wait_response: bool = True) -> Optional[str]:
        """Отправляет команду и возвращает ответ"""
        if not self.is_connected or not self.serial_port:
            self.error_occurred.emit("Порт не подключен")
            return None

        try:
            # Добавляем префикс и суффикс если нужно
            if not command.startswith("A007"):
                command = f"A007{command}"
            if not command.endswith("\n"):
                command += "\n"

            self.serial_port.write(command.encode())

            if wait_response:
                response = self.serial_port.readline().decode().strip()
                # Убираем префикс ответа если есть
                if response.startswith("A007"):
                    response = response[4:]
                return response
            return None

        except serial.SerialException as e:
            self.error_occurred.emit(f"Ошибка отправки команды: {str(e)}")
            return None

    @contextmanager
    def temporary_connection(self, port: str):
        """Контекстный менеджер для временного подключения"""
        was_connected = self.is_connected
        if not was_connected:
            if not self.connect_to_port(port):
                raise ConnectionError(f"Не удалось подключиться к {port}")
        try:
            yield
        finally:
            if not was_connected:
                self.disconnect()

# Продолжение следует...