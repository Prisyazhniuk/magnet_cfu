import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
import json
import csv
from datetime import datetime
from pathlib import Path


class DataBuffer(QObject):
    """
    Класс для буферизации данных с возможностью ограничения по времени или количеству точек
    """
    data_updated = pyqtSignal(dict)  # сигнал при обновлении данных

    def __init__(self, max_points: int = 1000, max_time_window: float = 10.0):
        super().__init__()
        self.max_points = max_points
        self.max_time_window = max_time_window
        self.data = {}  # ключ - имя канала, значение - deque из кортежей (time, value)
        self._timestamps = deque(maxlen=max_points)

    def add_data(self, channel: str, timestamp: float, value: float):
        """
        Добавление данных в буфер
        """
        if channel not in self.data:
            self.data[channel] = deque(maxlen=self.max_points)

        # Добавляем данные
        self.data[channel].append((timestamp, value))
        self._timestamps.append(timestamp)

        # Очистка старых данных по времени
        self._clean_old_data()

        # Сигнал о новом данных
        self.data_updated.emit({channel: self.get_channel_data(channel)})

    def _clean_old_data(self):
        """
        Удаление данных, выходящих за временное окно
        """
        if not self._timestamps:
            return

        current_time = self._timestamps[-1]
        threshold_time = current_time - self.max_time_window

        # Удаляем данные, которые слишком старые
        for channel in self.data:
            while self.data[channel] and self.data[channel][0][0] < threshold_time:
                self.data[channel].popleft()

    def get_channel_data(self, channel: str) -> Optional[np.ndarray]:
        """
        Получить данные канала в виде массива numpy [time, value]
        """
        if channel not in self.data or not self.data[channel]:
            return None

        return np.array(self.data[channel])

    def get_last_value(self, channel: str) -> Optional[float]:
        """
        Получить последнее значение канала
        """
        if channel not in self.data or not self.data[channel]:
            return None

        return self.data[channel][-1][1]

    def clear(self):
        """
        Очистка буфера
        """
        self.data.clear()
        self._timestamps.clear()


class DataProcessor(QObject):
    """
    Класс для обработки данных: фильтрация, усреднение, etc.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def moving_average(data: np.ndarray, window_size: int) -> np.ndarray:
        """
        Скользящее среднее
        """
        if len(data) < window_size:
            return data

        window = np.ones(window_size) / window_size
        return np.convolve(data, window, mode='valid')

    @staticmethod
    def filter_data(data: np.ndarray, filter_type: str = 'lowpass', **kwargs) -> np.ndarray:
        """
        Фильтрация данных (заглушка, можно расширить)
        """
        # TODO: реализовать фильтрацию
        return data

    @staticmethod
    def compute_fft(data: np.ndarray, sampling_rate: float) -> tuple:
        """
        Вычисление БПФ
        """
        n = len(data)
        fft_result = np.fft.fft(data)
        freqs = np.fft.fftfreq(n, 1 / sampling_rate)
        return freqs[:n // 2], np.abs(fft_result[:n // 2])


class DataExporter:
    """
    Класс для экспорта данных в различные форматы
    """

    @staticmethod
    def save_to_csv(filename: str, data: Dict[str, np.ndarray], metadata: Dict = None):
        """
        Сохранение данных в CSV файл
        """
        if not data:
            raise ValueError("No data to save")

        # Определяем общее время
        times = None
        for channel_data in data.values():
            if channel_data is not None and len(channel_data) > 0:
                times = channel_data[:, 0]
                break

        if times is None:
            raise ValueError("No valid data to save")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Записываем метаданные
            if metadata:
                writer.writerow(['# Metadata'])
                for key, value in metadata.items():
                    writer.writerow([f'# {key}', value])
                writer.writerow([])

            # Заголовок
            headers = ['Time']
            for channel_name in data.keys():
                if data[channel_name] is not None:
                    headers.append(channel_name)

            writer.writerow(headers)

            # Данные
            for i, time_val in enumerate(times):
                row = [time_val]
                for channel_data in data.values():
                    if channel_data is not None and i < len(channel_data):
                        row.append(channel_data[i, 1])
                    else:
                        row.append('')
                writer.writerow(row)

    @staticmethod
    def save_to_json(filename: str, data: Dict, metadata: Dict = None):
        """
        Сохранение данных в JSON файл
        """
        save_data = {
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }

        for channel_name, channel_data in data.items():
            if channel_data is not None:
                save_data['data'][channel_name] = {
                    'time': channel_data[:, 0].tolist(),
                    'values': channel_data[:, 1].tolist()
                }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def auto_save(data: Dict[str, np.ndarray], base_filename: str = "measurement"):
        """
        Автоматическое сохранение с генерацией имени файла
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.csv"

        metadata = {
            'created': datetime.now().isoformat(),
            'channels': list(data.keys())
        }

        DataExporter.save_to_csv(filename, data, metadata)
        return filename