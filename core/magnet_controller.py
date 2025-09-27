import serial
import serial.tools.list_ports
from contextlib import contextmanager
from typing import List, Optional, Dict
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
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


class MagnetController(QObject):
    """
    Контроллер для управления электромагнитом через последовательный порт
    """

    # Сигналы
    connection_changed = pyqtSignal(bool)
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    current_changed = pyqtSignal(float)  # Сигнал об изменении тока

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_port = None
        self._is_connected = False

    def get_available_ports(self) -> List[str]:
        """Получение списка доступных COM-портов"""
        ports = []
        for port in serial.tools.list_ports.comports():
            try:
                # Пытаемся открыть порт для проверки доступности
                test_port = serial.Serial(port.device, timeout=0.1)
                test_port.close()
                ports.append(port.device)
            except (serial.SerialException, OSError):
                # Порт недоступен, пропускаем
                continue
        return ports

    def _get_parity_constant(self, parity_str: str):
        """Преобразование строки parity в константу pyserial"""
        parity_map = {
            'No Parity': serial.PARITY_NONE,
            'Even Parity': serial.PARITY_EVEN,
            'Odd Parity': serial.PARITY_ODD,
            'Space Parity': serial.PARITY_SPACE,
            'Mark Parity': serial.PARITY_MARK,
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD,
            'S': serial.PARITY_SPACE,
            'M': serial.PARITY_MARK
        }
        return parity_map.get(parity_str, serial.PARITY_NONE)

    def _get_stopbits_constant(self, stopbits_str: str):
        """Преобразование строки stopbits в константу pyserial"""
        stopbits_map = {
            'One Stop': serial.STOPBITS_ONE,
            'One And Half Stop': serial.STOPBITS_ONE_POINT_FIVE,
            'Two Stop': serial.STOPBITS_TWO,
            '1': serial.STOPBITS_ONE,
            '1.5': serial.STOPBITS_ONE_POINT_FIVE,
            '2': serial.STOPBITS_TWO
        }
        return stopbits_map.get(stopbits_str, serial.STOPBITS_ONE)

    def connect(self, port: str, baudrate: int = None) -> bool:
        """Подключение к магниту"""
        try:
            # Проверяем доступность порта
            if port not in self.get_available_ports():
                self.error_occurred.emit(f"Порт {port} недоступен")
                return False

            if baudrate is None:
                baudrate = app_settings.get("serial.baud_rate", 115200)

            # Получаем настройки из конфигурации
            data_bits = app_settings.get("serial.data_bits", 8)
            parity_str = app_settings.get("serial.parity", "No Parity")
            stopbits_str = app_settings.get("serial.stop_bits", "One Stop")

            # Преобразуем в константы pyserial
            parity = self._get_parity_constant(parity_str)
            stopbits = self._get_stopbits_constant(stopbits_str)

            print(f"Attempting connection with parameters:")
            print(f"  Port: {port}")
            print(f"  Baudrate: {baudrate}")
            print(f"  Data bits: {data_bits}")
            print(f"  Parity: {parity_str} ({parity})")
            print(f"  Stop bits: {stopbits_str} ({stopbits})")

            # Создаем подключение с правильными параметрами
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=data_bits,
                parity=parity,
                stopbits=stopbits,
                timeout=app_settings.get("serial.timeout", 1),
                xonxoff=False,  # Отключаем программное управление потоком
                rtscts=False,  # Отключаем аппаратное управление потоком
                dsrdtr=False  # Отключаем DSR/DTR
            )

            # Проверяем, что порт открылся
            if not self.serial_port.is_open:
                self.error_occurred.emit("Не удалось открыть порт")
                return False

            self._is_connected = True
            self.connection_changed.emit(True)

            # Инициализация магнита
            self._initialize_magnet()

            print(f"Successfully connected to {port}")
            return True

        except serial.SerialException as e:
            error_msg = f"Ошибка последовательного порта: {str(e)}"
            self.error_occurred.emit(error_msg)
            print(f"Serial error: {e}")
            self._is_connected = False
            return False

        except OSError as e:
            error_msg = f"Ошибка системы: {str(e)}"
            self.error_occurred.emit(error_msg)
            print(f"OS error: {e}")
            self._is_connected = False
            return False

        except Exception as e:
            error_msg = f"Неожиданная ошибка подключения: {str(e)}"
            self.error_occurred.emit(error_msg)
            print(f"Unexpected error: {e}")
            self._is_connected = False
            return False

    def _initialize_magnet(self):
        """Инициализация магнита после подключения"""
        try:
            # Небольшая задержка после подключения
            import time
            time.sleep(0.2)

            # Очищаем буферы
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            # Отправляем простую команду для проверки связи
            print("Testing communication...")
            test_response = self.send_command("*IDN?", retries=3, delay=0.2)
            if test_response:
                print(f"Device responded: {test_response}")
            else:
                print("Warning: Device did not respond to IDN command during initialization")

            # Отправляем базовые команды инициализации
            # Некоторые команды не дают ответа, поэтому для них wait_response=False
            init_commands = [
                ("*CLS", "Clear status", False),  # Не ждем ответа
                ("SYST:REM", "Remote mode", False),  # Не ждем ответа
                ("OUTP ON", "Enable output", False),  # Не ждем ответа
                ("*POL 1", "Set polarity to positive", False)  # Не ждем ответа
            ]

            for cmd, description, wait_response in init_commands:
                print(f"Initializing: {description}")
                result = self.send_command(cmd, wait_response=wait_response, retries=0, delay=0.1)
                if wait_response and result is not None:
                    print(f"  Response: '{result}'")
                else:
                    print(f"  Command sent (no response expected)")
                time.sleep(0.2)  # Задержка между командами

            print("Magnet initialization completed")

        except Exception as e:
            print(f"Ошибка инициализации магнита: {e}")
            # Не прерываем подключение из-за ошибок инициализации

    def disconnect(self):
        """Отключение от магнита"""
        if self.serial_port and self.serial_port.is_open:
            try:
                print("Disconnecting from magnet...")
                # Безопасное отключение с повторными попытками
                self.send_command("OUTP OFF", wait_response=False, retries=1, delay=0.1)

                # Небольшая задержка перед сбросом
                import time
                time.sleep(0.2)

                self.send_command("*RST", wait_response=False, retries=1, delay=0.1)

                # Задержка перед закрытием порта
                time.sleep(0.2)

            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                try:
                    self.serial_port.close()
                    print("Serial port closed")
                except:
                    pass

        self._is_connected = False
        self.connection_changed.emit(False)
        print("Disconnected from magnet")

    @property
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self._is_connected and self.serial_port and self.serial_port.is_open

    def send_command(self, command: str, wait_response: bool = True, retries: int = 2, delay: float = 0.1) -> Optional[
        str]:
        """Отправка команды магниту с повторными попытками"""
        if not self.is_connected:
            print(f"Cannot send command '{command}': not connected")
            return None

        max_attempts = max(1, retries + 1)  # Минимум одна попытка

        for attempt in range(max_attempts):
            try:
                # Небольшая задержка между командами для стабильности
                if attempt > 0:
                    import time
                    time.sleep(delay * attempt)  # Увеличиваем задержку с каждой попыткой

                # Очищаем входной буфер перед отправкой
                self.serial_port.reset_input_buffer()

                # Форматирование команды
                formatted_command = command
                if not formatted_command.startswith("A007"):
                    formatted_command = f"A007{formatted_command}"
                if not formatted_command.endswith("\n"):
                    formatted_command += "\n"

                print(f"Sending command (attempt {attempt + 1}): {formatted_command.strip()}")
                self.serial_port.write(formatted_command.encode('utf-8'))
                self.serial_port.flush()  # Принудительная отправка

                if wait_response:
                    # Даем устройству время на обработку команды
                    import time
                    time.sleep(0.05)  # 50мс задержка

                    # Читаем ответ с увеличенным таймаутом
                    original_timeout = self.serial_port.timeout
                    self.serial_port.timeout = 2.0  # Увеличиваем таймаут до 2 секунд

                    response = self.serial_port.readline().decode('utf-8').strip()
                    self.serial_port.timeout = original_timeout  # Восстанавливаем исходный таймаут

                    print(f"Received response (attempt {attempt + 1}): '{response}'")

                    # Если получили непустой ответ
                    if response:
                        # Убираем префикс ответа если есть
                        if response.startswith("A007"):
                            response = response[4:]
                        return response
                    elif attempt == (max_attempts - 1):
                        # Последняя попытка, возвращаем пустую строку
                        print(f"No response after {max_attempts} attempts")
                        return ""
                else:
                    # Команда без ответа - просто возвращаем None после отправки
                    return None

            except UnicodeDecodeError as e:
                print(f"Unicode decode error (attempt {attempt + 1}): {e}")
                if attempt == (max_attempts - 1):
                    self.error_occurred.emit(f"Ошибка декодирования ответа: {str(e)}")
                continue

            except serial.SerialTimeoutException:
                print(f"Serial timeout (attempt {attempt + 1})")
                if attempt == (max_attempts - 1):
                    self.error_occurred.emit("Таймаут ожидания ответа")
                continue

            except Exception as e:
                print(f"Command error (attempt {attempt + 1}): {e}")
                if attempt == (max_attempts - 1):
                    self.error_occurred.emit(f"Ошибка команды {command}: {str(e)}")
                continue

        return None

    def set_current(self, current: float) -> bool:
        """Установка тока"""
        if not self.is_connected:
            print("Cannot set current: not connected")
            return False

        try:
            # Определяем полярность
            polarity = 2 if current < 0 else 1
            print(f"Setting current: {current}A, polarity: {polarity}")

            # Устанавливаем полярность (команда без ответа)
            self.send_command(f"*POL {polarity}", wait_response=False, retries=0, delay=0.1)
            print(f"Polarity command sent: {polarity}")

            # Небольшая задержка после установки полярности
            import time
            time.sleep(0.2)

            # Для AKIP-1134 попробуем другие варианты команд
            # Сначала пробуем стандартные SCPI команды
            voltage = abs(current) * 10  # Предполагаем сопротивление 10 Ом

            # Пробуем разные варианты команд
            commands_to_try = [
                f"CURR {abs(current):.3f}",  # Простая команда тока
                f"SOUR:CURR {abs(current):.3f}",  # Стандартная SCPI
                f"SOUR:VOLT {voltage:.3f};CURR {abs(current):.3f}",  # Комбинированная
                f"APPL {abs(current):.3f}",  # Команда применения
            ]

            for cmd in commands_to_try:
                print(f"Trying current command: {cmd}")
                self.send_command(cmd, wait_response=False, retries=0, delay=0.1)
                time.sleep(0.3)  # Даем время на обработку

                # Проверяем, сработала ли команда
                measurements = self.read_measurements()
                if measurements and abs(measurements.get('current', 0)) > 0.001:
                    print(f"Command successful: {cmd}")
                    self.current_changed.emit(current)
                    return True

            print("All current commands failed")
            return False

        except Exception as e:
            self.error_occurred.emit(f"Ошибка установки тока {current}A: {str(e)}")
            print(f"Set current error: {e}")
            return False

    def set_current_smooth(self, target_current: float, step: float = 0.01) -> bool:
        """Плавная установка тока с заданным шагом"""
        if not self.is_connected:
            return False

        try:
            # Читаем текущий ток
            current_data = self.read_measurements()
            current_now = current_data.get('current', 0) if current_data else 0

            # Определяем направление и шаги
            if target_current > current_now:
                steps = list(decimal_range(current_now, target_current + step, step))
            else:
                steps = list(rev_decimal_range(current_now, target_current - step, step))

            # Плавно изменяем ток
            for current in steps:
                if not self.set_current(current):
                    return False

            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка плавной установки тока: {str(e)}")
            return False

    def read_measurements(self) -> Dict[str, float]:
        """Чтение текущих измерений"""
        if not self.is_connected:
            print("Cannot read measurements: not connected")
            return {}

        response = self.send_command("FETC?")
        if response:
            try:
                print(f"Raw measurement response: {response}")
                parts = response.split(',')
                if len(parts) >= 2:
                    voltage = float(parts[0])
                    current = float(parts[1])

                    # Корректировка знака тока в зависимости от полярности
                    polarity_response = self.send_command("*POL?")
                    if polarity_response and "2" in polarity_response:
                        current = -current

                    result = {'voltage': voltage, 'current': current}
                    print(f"Parsed measurements: {result}")
                    return result
            except ValueError as e:
                self.error_occurred.emit(f"Ошибка парсинга измерений: {e}")
                print(f"Parse error: {e}")

        print("No valid measurements received")
        return {}

    def send_idn_command(self) -> Optional[str]:
        """Отправка команды идентификации с повышенной надежностью"""
        print("Requesting device identification...")
        return self.send_command("*IDN?", retries=3, delay=0.2)

    @contextmanager
    def temporary_connection(self, port: str):
        """Контекстный менеджер для временного подключения"""
        was_connected = self._is_connected
        if not was_connected:
            if not self.connect(port):
                raise ConnectionError(f"Не удалось подключиться к {port}")
        try:
            yield
        finally:
            if not was_connected:
                self.disconnect()