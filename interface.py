import os
import sys
import time
import numpy as np
import pyqtgraph as pg

from pathlib import Path
from zhinst.toolkit import Session
from zhinst.core import ziListEnum, ziDiscovery, ziDAQServer
from PyQt5.QtCore import QTimer, Qt, QIODevice, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QWidget,
    QDoubleSpinBox,
    QGroupBox,
    QSpinBox,
    QComboBox
)


class MagnetCFU(QMainWindow):
    simulate_mode = True  # Флаг для режима симуляции (без оборудования)
    upd_freq = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        # Инициализация интерфейса
        self.init_ui()

        # Если включен "режим симуляции", пропускаем настройки аппаратуры
        if not self.simulate_mode:
            self.discovery = ziDiscovery()
            self.device = self.discovery.find('mf-dev4999').lower()
            self.configure_device()
        else:
            self.device = "simulation-device"
            print("Simulation mode enabled. Hardware calls will be skipped.")

    def init_ui(self):
        """Инициализация интерфейса и основных элементов."""
        # Графики
        self.graph_widget = pg.PlotWidget()
        self.hysteresis_graph = pg.PlotWidget()

        # Таймеры
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_and_update_data)  # Чтение данных каждые 100 мс
        self.timer.start(100)

        # Настройка интерфейса
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)
        layout.addWidget(self.hysteresis_graph)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # Инициализация компонентов графиков
        self.init_plot_widgets()

    def init_plot_widgets(self):
        """Инициализация настроек для графиков."""
        styles = {"color": "#FFFFFF", "font-size": "10px"}
        # Первый график: реальное время
        self.graph_widget.setBackground("w")
        self.graph_widget.setLabel("left", "Voltage (U)", **styles)
        self.graph_widget.setLabel("bottom", "Time (s)", **styles)

        # Второй график: гистерезис
        self.hysteresis_graph.setBackground("w")
        self.hysteresis_graph.setLabel("left", "Voltage (U)", **styles)
        self.hysteresis_graph.setLabel("bottom", "Current (I)", **styles)

    def configure_device(self):
        """Настройка устройства с использованием аппаратных методов."""
        self.api_lvl = 6
        self.dev_prop = self.discovery.get(self.device)
        self.serveraddress = self.dev_prop["serveraddress"]
        self.serverport = self.dev_prop["serverport"]
        self.serverversion = self.dev_prop["serverversion"]
        self.daq = ziDAQServer(self.serveraddress, self.serverport, self.api_lvl)
        self.daq_module = self.daq.dataAcquisitionModule()
        self.daq.unsubscribe("*")  # Очистка подписки

    def read_and_update_data(self):
        """Считывание данных с устройства и обновление графиков."""
        if self.simulate_mode:
            # В режиме симуляции генерируем случайные значения
            t = np.linspace(0, 10, 100)
            voltages = np.sin(t) + np.random.normal(0, 0.1, size=len(t))
            currents = np.cos(t) + np.random.normal(0, 0.1, size=len(t))
        else:
            # Реальная обработка данных с устройства
            t, voltages, currents = self.get_device_data()

        # График в реальном времени
        self.graph_widget.plot(t, voltages, pen="b", clear=True)

        # График гистерезиса
        self.hysteresis_graph.plot(currents, voltages, pen="r", clear=True)

    def get_device_data(self):
        """Получение данных в реальном времени с устройства."""
        # Обработка данных реального времени (пример)
        timestamp0 = time.time()
        t = np.linspace(0, 10, 100)
        voltages = np.sin(t) + np.random.normal(0, 0.1, size=len(t))
        currents = np.cos(t) + np.random.normal(0, 0.1, size=len(t))

        return t, voltages, currents


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MagnetCFU()
    window.setWindowTitle("Magnet Control UI")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
