import numpy as np
from collections import deque
from typing import Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class CircularBuffer:
    """
    Кольцевой буфер для эффективного хранения данных с фиксированным размером
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.size = 0

    def append(self, item: Any):
        """Добавление элемента в буфер"""
        self.buffer.append(item)
        self.size = len(self.buffer)

    def get_all(self) -> list:
        """Получение всех элементов буфера"""
        return list(self.buffer)

    def clear(self):
        """Очистка буфера"""
        self.buffer.clear()
        self.size = 0

    def is_full(self) -> bool:
        """Проверка заполненности буфера"""
        return self.size == self.capacity

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        return self.buffer[index]


class DataProcessor(QObject):
    """
    Класс для обработки и анализа данных
    """

    # Сигналы для уведомления о результатах обработки
    processing_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def moving_average(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """
        Скользящее среднее
        """
        if len(data) < window_size:
            return data

        weights = np.ones(window_size) / window_size
        return np.convolve(data, weights, mode='valid')

    def low_pass_filter(self, data: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        """
        Простой низкочастотный фильтр (экспоненциальное сглаживание)
        """
        filtered = np.zeros_like(data)
        filtered[0] = data[0]

        for i in range(1, len(data)):
            filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i - 1]

        return filtered

    def calculate_derivative(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Вычисление производной dy/dx
        """
        if len(x) != len(y):
            raise ValueError("Arrays x and y must have the same length")

        if len(x) < 2:
            return np.array([0])

        derivative = np.gradient(y, x)
        return derivative

    def find_peaks(self, data: np.ndarray, threshold: float = 0.5, min_distance: int = 1) -> np.ndarray:
        """
        Поиск пиков в данных
        """
        if len(data) == 0:
            return np.array([])

        peaks = []
        max_val = np.max(data)

        for i in range(1, len(data) - 1):
            if (data[i] > data[i - 1] and data[i] > data[i + 1] and
                    data[i] > threshold * max_val):
                peaks.append(i)

        # Фильтрация по минимальному расстоянию
        if min_distance > 1 and peaks:
            filtered_peaks = [peaks[0]]
            for peak in peaks[1:]:
                if peak - filtered_peaks[-1] >= min_distance:
                    filtered_peaks.append(peak)
            peaks = filtered_peaks

        return np.array(peaks)

    def calculate_rms(self, data: np.ndarray) -> float:
        """
        Вычисление среднеквадратичного значения
        """
        return np.sqrt(np.mean(np.square(data)))

    def normalize_data(self, data: np.ndarray) -> np.ndarray:
        """
        Нормализация данных к диапазону [0, 1]
        """
        if np.max(data) == np.min(data):
            return np.zeros_like(data)
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    def remove_outliers(self, data: np.ndarray, std_threshold: float = 2.0) -> np.ndarray:
        """
        Удаление выбросов на основе стандартного отклонения
        """
        if len(data) == 0:
            return data

        mean = np.mean(data)
        std = np.std(data)

        # Замена выбросов на среднее значение
        cleaned_data = data.copy()
        outliers = np.abs(data - mean) > std_threshold * std
        cleaned_data[outliers] = mean

        return cleaned_data

    def interpolate_data(self, x: np.ndarray, y: np.ndarray, new_x: np.ndarray) -> np.ndarray:
        """
        Интерполяция данных на новые точки x
        """
        if len(x) < 2:
            return np.full_like(new_x, y[0] if len(y) > 0 else 0)

        return np.interp(new_x, x, y)

    def process_in_background(self, data: np.ndarray, operation: str, **kwargs):
        """
        Обработка данных в фоновом режиме (может быть запущена в отдельном потоке)
        """
        try:
            if operation == 'moving_average':
                result = self.moving_average(data, kwargs.get('window_size', 5))
            elif operation == 'low_pass':
                result = self.low_pass_filter(data, kwargs.get('alpha', 0.1))
            elif operation == 'normalize':
                result = self.normalize_data(data)
            elif operation == 'remove_outliers':
                result = self.remove_outliers(data, kwargs.get('std_threshold', 2.0))
            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.processing_complete.emit(result)

        except Exception as e:
            self.error_occurred.emit(f"Processing error: {str(e)}")
