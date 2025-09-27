import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor
from typing import Dict, Optional


class CustomPlotWidget(pg.PlotWidget):
    """
    Кастомный виджет графика с дополнительными функциями
    """
    point_clicked = pyqtSignal(float, float)  # сигнал при клике на точку

    def __init__(self, parent=None, title="", x_label="", y_label=""):
        super().__init__(parent)
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.setup_plot()

    def setup_plot(self):
        self.setLabel('left', self.y_label)
        self.setLabel('bottom', self.x_label)
        self.showGrid(x=True, y=True, alpha=0.3)
        self.addLegend()

    def mousePressEvent(self, event):
        """
        Перехват клика мыши для эмитации сигнала
        """
        if event.button() == 1:  # левая кнопка мыши
            pos = self.plotItem.vb.mapSceneToView(event.pos())
            self.point_clicked.emit(pos.x(), pos.y())
        super().mousePressEvent(event)


class LockInPlotWidget(CustomPlotWidget):
    """
    Виджет для отображения данных Lock-in
    """

    def __init__(self, parent=None):
        super().__init__(parent, "Lock-in Data", "Time, s", "Voltage, V")
        self.data_lines = {}
        self.time_data = np.array([])
        self.x_data = np.array([])
        self.y_data = np.array([])

    def update_plot(self, time_data, x_data, y_data):
        """
        Обновление графика
        """
        if time_data is None or x_data is None or y_data is None:
            return

        self.time_data = time_data
        self.x_data = x_data
        self.y_data = y_data

        if "X" not in self.data_lines:
            self.data_lines["X"] = self.plot(pen=pg.mkPen(color='r', width=2), name="X")
        if "Y" not in self.data_lines:
            self.data_lines["Y"] = self.plot(pen=pg.mkPen(color='b', width=2), name="Y")

        self.data_lines["X"].setData(time_data, x_data)
        self.data_lines["Y"].setData(time_data, y_data)

    def clear_plot(self):
        """
        Очистка графика
        """
        for line in self.data_lines.values():
            line.clear()
        self.data_lines.clear()
        self.time_data = np.array([])
        self.x_data = np.array([])
        self.y_data = np.array([])


class HysteresisPlotWidget(CustomPlotWidget):
    """
    Виджет для отображения петли гистерезиса
    """

    def __init__(self, parent=None):
        super().__init__(parent, "Hysteresis", "Current, A", "Voltage, V")
        self.curve = self.plot(pen=pg.mkPen(color='g', width=2))

    def update_plot(self, current_data, voltage_data):
        """
        Обновление графика гистерезиса
        """
        if current_data is None or voltage_data is None:
            return

        self.curve.setData(current_data, voltage_data)

    def clear_plot(self):
        self.curve.clear()


class RealTimePlotManager(QObject):
    """
    Менеджер для управления реальным временем графиков
    """

    def __init__(self, lockin_plot: LockInPlotWidget, hysteresis_plot: HysteresisPlotWidget):
        super().__init__()
        self.lockin_plot = lockin_plot
        self.hysteresis_plot = hysteresis_plot
        self.data_buffer = {}
        self.is_endless_mode = False
        self.time_window = 10.0  # секунд

    def update_lockin_data(self, new_data: Dict):
        """
        Обновление данных Lock-in
        """
        # Обработка данных X и Y каналов
        for path, data in new_data.items():
            if 'x' in path.lower():
                self._update_channel('X', data)
            elif 'y' in path.lower():
                self._update_channel('Y', data)

    def _update_channel(self, channel: str, data: Dict):
        """
        Обновление данных конкретного канала
        """
        if channel not in self.data_buffer:
            self.data_buffer[channel] = {'time': np.array([]), 'values': np.array([])}

        # Добавляем новые данные
        time_val = data.get('time_relative', 0)
        value = data.get('value', 0)

        buffer = self.data_buffer[channel]
        buffer['time'] = np.append(buffer['time'], time_val)
        buffer['values'] = np.append(buffer['values'], value)

        # Применяем режим отображения
        if not self.is_endless_mode:
            self._apply_time_window(buffer)

        # Обновляем график
        if channel == 'X':
            self.lockin_plot.update_plot(buffer['time'], buffer['values'], None)
        elif channel == 'Y':
            # Нужно обновить оба канала
            x_buffer = self.data_buffer.get('X', {'time': np.array([]), 'values': np.array([])})
            y_buffer = self.data_buffer.get('Y', {'time': np.array([]), 'values': np.array([])})

            # Синхронизируем временные метки
            min_len = min(len(x_buffer['time']), len(y_buffer['time']))
            if min_len > 0:
                time_data = x_buffer['time'][-min_len:]
                x_data = x_buffer['values'][-min_len:]
                y_data = y_buffer['values'][-min_len:]
                self.lockin_plot.update_plot(time_data, x_data, y_data)

    def _apply_time_window(self, buffer: Dict):
        """
        Применение временного окна к данным
        """
        if len(buffer['time']) == 0:
            return

        current_time = buffer['time'][-1]
        mask = buffer['time'] >= (current_time - self.time_window)

        buffer['time'] = buffer['time'][mask]
        buffer['values'] = buffer['values'][mask]

    def set_endless_mode(self, enabled: bool):
        """
        Установка режима бесконечного отображения
        """
        self.is_endless_mode = enabled
        if enabled:
            self.lockin_plot.enableAutoRange(axis='x', enable=True)
        else:
            self.lockin_plot.setXRange(-self.time_window, 0, padding=0)

    def clear_all(self):
        """
        Очистка всех данных
        """
        self.data_buffer.clear()
        self.lockin_plot.clear_plot()
        self.hysteresis_plot.clear_plot()
