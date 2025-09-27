from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QTime
import numpy as np
from typing import Dict, List, Optional
import time


class HysteresisMeasurement(QObject):
    """
    Класс для управления измерением петли гистерезиса
    Координирует работу магнита и lock-in усилителя
    """

    # Сигналы
    measurement_started = pyqtSignal()
    measurement_finished = pyqtSignal()
    measurement_paused = pyqtSignal()
    measurement_resumed = pyqtSignal()
    data_point_acquired = pyqtSignal(dict)  # {current, voltage, x, y, r, phase, timestamp}
    progress_updated = pyqtSignal(float)  # Процент выполнения (0-100)
    status_message = pyqtSignal(str)  # Сообщения о статусе
    error_occurred = pyqtSignal(str)

    def __init__(self, magnet_controller, lockin_controller, parent=None):
        super().__init__(parent)
        self.magnet = magnet_controller
        self.lockin = lockin_controller

        # Параметры измерения
        self.params = {}
        self.is_measuring = False
        self.is_paused = False

        # Данные измерения
        self.data_points = []
        self.current_loop = 0
        self.total_loops = 1

        # Текущее состояние измерения
        self.current_direction = 1  # 1 - вперед, -1 - назад
        self.current_target = 0
        self.measurement_sequence = []
        self.current_step_index = 0

        # Таймеры - УБИРАЕМ ненужный таймер
        # self.measurement_timer = QTimer()  # УДАЛЯЕМ эту строку
        # self.measurement_timer.timeout.connect(self._measurement_step)  # УДАЛЯЕМ эту строку

        self.settling_timer = QTimer()
        self.settling_timer.setSingleShot(True)
        self.settling_timer.timeout.connect(self._after_settling)

        # Буферы для синхронизации данных
        self.pending_current = None
        self.last_lockin_data = None
        self.waiting_for_settling = False

    def start_measurement(self, parameters: Dict):
        """
        Запуск измерения гистерезиса

        Parameters:
        - start_current: начальный ток (A)
        - stop_current: конечный ток (A)
        - step: шаг изменения тока (A)
        - loops: количество циклов
        - interval: интервал между точками (ms)
        - settling_time: время установления после изменения тока (ms)
        """
        if self.is_measuring:
            self.error_occurred.emit("Измерение уже запущено")
            return False

        # Валидация параметров
        if not self._validate_parameters(parameters):
            return False

        self.params = parameters.copy()
        self.total_loops = parameters.get('loops', 1)
        self.current_loop = 0
        self.data_points = []
        self.is_measuring = True
        self.is_paused = False

        # Генерация последовательности измерения
        if not self._generate_measurement_sequence():
            return False

        self.current_step_index = 0

        # Запускаем сбор данных с lock-in
        if self.lockin.is_connected:
            try:
                self.lockin.start_acquisition()
                self.status_message.emit("Lock-in: сбор данных запущен")
            except Exception as e:
                self.error_occurred.emit(f"Ошибка запуска lock-in: {str(e)}")
                return False

        # Начинаем измерение
        self.status_message.emit("Запуск измерения гистерезиса...")
        self.measurement_started.emit()

        # Запускаем первый шаг
        self._execute_next_step()

        return True

    def _validate_parameters(self, parameters: Dict) -> bool:
        """Проверка корректности параметров измерения"""
        required = ['start_current', 'stop_current', 'step']
        for param in required:
            if param not in parameters:
                self.error_occurred.emit(f"Отсутствует параметр: {param}")
                return False

        if parameters['step'] <= 0:
            self.error_occurred.emit("Шаг должен быть положительным")
            return False

        if parameters['loops'] < 1:
            self.error_occurred.emit("Количество циклов должно быть ≥ 1")
            return False

        return True

    def _generate_measurement_sequence(self) -> bool:
        """Генерация последовательности шагов измерения"""
        self.measurement_sequence = []
        start = self.params['start_current']
        stop = self.params['stop_current']
        step = self.params['step']

        # Определяем направление
        if start == stop:
            self.error_occurred.emit("Начальный и конечный токи не могут быть равны")
            return False

        direction = 1 if stop > start else -1

        # Генерируем последовательность для одного цикла
        # Прямой ход: start -> stop
        current = start
        while (direction > 0 and current <= stop) or (direction < 0 and current >= stop):
            self.measurement_sequence.append({
                'current': current,
                'direction': 1  # Прямой ход
            })
            current += step * direction

        # Обеспечиваем попадание в конечную точку
        if self.measurement_sequence[-1]['current'] != stop:
            self.measurement_sequence.append({
                'current': stop,
                'direction': 1
            })

        # Обратный ход: stop -> start
        current = stop
        while (direction > 0 and current >= start) or (direction < 0 and current <= start):
            self.measurement_sequence.append({
                'current': current,
                'direction': -1  # Обратный ход
            })
            current -= step * direction

        # Обеспечиваем попадание в начальную точку
        if self.measurement_sequence[-1]['current'] != start:
            self.measurement_sequence.append({
                'current': start,
                'direction': -1
            })

        self.status_message.emit(f"Сгенерировано {len(self.measurement_sequence)} шагов измерения")
        return True

    def _execute_next_step(self):
        """Выполнение следующего шага измерения"""
        if not self.is_measuring or self.is_paused:
            return

        if self.current_step_index >= len(self.measurement_sequence):
            # Завершаем текущий цикл
            self.current_loop += 1
            if self.current_loop >= self.total_loops:
                self._finish_measurement()
                return
            else:
                # Начинаем следующий цикл
                self.current_step_index = 0
                self.status_message.emit(f"Начало цикла {self.current_loop + 1}/{self.total_loops}")

        step = self.measurement_sequence[self.current_step_index]
        self.pending_current = step['current']

        # Устанавливаем ток
        try:
            success = self.magnet.set_current(self.pending_current)
            if not success:
                self.error_occurred.emit(f"Ошибка установки тока: {self.pending_current} A")
                self.stop_measurement()
                return

            self.status_message.emit(
                f"Цикл {self.current_loop + 1}/{self.total_loops}, "
                f"Шаг {self.current_step_index + 1}/{len(self.measurement_sequence)}: "
                f"{self.pending_current:.3f} A"
            )

            # Ждем время установления
            settling_time = self.params.get('settling_time', 1000)
            self.waiting_for_settling = True
            self.settling_timer.start(settling_time)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка выполнения шага: {str(e)}")
            self.stop_measurement()

    def _after_settling(self):
        """Действия после времени установления"""
        if not self.waiting_for_settling or not self.is_measuring or self.is_paused:
            return

        self.waiting_for_settling = False

        try:
            # Читаем данные с магнита
            magnet_data = self.magnet.read_measurements()
            if not magnet_data:
                self.error_occurred.emit("Не удалось получить данные с магнита")
                self._advance_to_next_step()  # Продолжаем несмотря на ошибку
                return

            # Создаем точку данных
            data_point = {
                'current': magnet_data['current'],
                'voltage': magnet_data['voltage'],
                'timestamp': time.time(),
                'loop': self.current_loop + 1,
                'direction': self.measurement_sequence[self.current_step_index]['direction'],
                'step_index': self.current_step_index
            }

            # Добавляем данные lock-in если доступны
            if self.last_lockin_data:
                data_point.update(self.last_lockin_data)

            self.data_points.append(data_point)
            self.data_point_acquired.emit(data_point)

            # Обновляем прогресс
            total_steps = len(self.measurement_sequence) * self.total_loops
            completed_steps = self.current_step_index + len(self.measurement_sequence) * self.current_loop
            progress = (completed_steps / total_steps) * 100
            self.progress_updated.emit(min(progress, 100.0))

            # Переходим к следующему шагу
            self._advance_to_next_step()

        except Exception as e:
            self.error_occurred.emit(f"Ошибка сбора данных: {str(e)}")
            self._advance_to_next_step()  # Продолжаем измерение

    def _advance_to_next_step(self):
        """Переход к следующему шагу измерения"""
        self.current_step_index += 1

        # Запускаем следующий шаг после интервала
        interval = self.params.get('interval', 1000)
        QTimer.singleShot(interval, self._execute_next_step)

    def pause_measurement(self):
        """Приостановка измерения"""
        if self.is_measuring and not self.is_paused:
            self.is_paused = True
            self.settling_timer.stop()  # Останавливаем таймер установления
            self.measurement_paused.emit()
            self.status_message.emit("Измерение приостановлено")

    def resume_measurement(self):
        """Возобновление измерения"""
        if self.is_measuring and self.is_paused:
            self.is_paused = False
            self.measurement_resumed.emit()
            self.status_message.emit("Измерение возобновлено")
            self._execute_next_step()

    def stop_measurement(self):
        """Остановка измерения"""
        if not self.is_measuring:
            return

        self.is_measuring = False
        self.is_paused = False
        self.waiting_for_settling = False

        # Останавливаем таймеры
        self.settling_timer.stop()

        # Останавливаем устройства
        try:
            if self.lockin.is_connected:
                self.lockin.stop_acquisition()
        except:
            pass

        # Возвращаем ток в ноль
        try:
            self.magnet.set_current(0)
        except:
            pass

        self.status_message.emit("Измерение остановлено")
        self.measurement_finished.emit()

    def _finish_measurement(self):
        """Завершение измерения"""
        self.is_measuring = False
        self.waiting_for_settling = False

        # Останавливаем устройства
        try:
            if self.lockin.is_connected:
                self.lockin.stop_acquisition()
        except:
            pass

        self.status_message.emit(f"Измерение завершено. Собрано {len(self.data_points)} точек")
        self.progress_updated.emit(100.0)
        self.measurement_finished.emit()

    def update_lockin_data(self, data: Dict):
        """Обновление данных от lock-in усилителя"""
        try:
            x_value = 0
            y_value = 0

            for path, values in data.items():
                if '.x' in path.lower():
                    x_value = values.get('value', 0)
                elif '.y' in path.lower():
                    y_value = values.get('value', 0)

            self.last_lockin_data = {
                'x': x_value,
                'y': y_value,
                'r': np.sqrt(x_value ** 2 + y_value ** 2),
                'phase': np.arctan2(y_value, x_value) * 180 / np.pi if x_value != 0 else 0
            }
        except Exception as e:
            print(f"Ошибка обработки данных lock-in: {e}")

    def get_data(self) -> List[Dict]:
        """Получение накопленных данных"""
        return self.data_points.copy()

    def clear_data(self):
        """Очистка данных измерения"""
        self.data_points.clear()

    def save_data(self, filename: str, format: str = 'csv'):
        """Сохранение данных в файл"""
        if not self.data_points:
            self.error_occurred.emit("Нет данных для сохранения")
            return False

        try:
            if format.lower() == 'csv':
                self._save_csv(filename)
            elif format.lower() == 'json':
                self._save_json(filename)
            else:
                self.error_occurred.emit(f"Неизвестный формат: {format}")
                return False

            self.status_message.emit(f"Данные сохранены в {filename}")
            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка сохранения: {str(e)}")
            return False

    def _save_csv(self, filename: str):
        """Сохранение в CSV формате"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if self.data_points:
                fieldnames = self.data_points[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data_points)

    def _save_json(self, filename: str):
        """Сохранение в JSON формате"""
        import json

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'parameters': self.params,
                'data_points': self.data_points,
                'timestamp': time.time(),
                'data_points_count': len(self.data_points)
            }, f, indent=2, ensure_ascii=False)
