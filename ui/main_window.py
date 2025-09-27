import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTabWidget, QStatusBar, QLabel, QMessageBox, QSplitter,
                             QProgressBar)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

from core.magnet_controller import MagnetController
from core.lockin_controller import LockInController
from core.data_manager import DataBuffer, DataExporter
from core.hysteresis_measurement import HysteresisMeasurement  # Добавляем импорт
from widgets.plots import LockInPlotWidget, HysteresisPlotWidget, RealTimePlotManager
from ui.control_tab import ControlTab
from ui.config_tab import ConfigTab
from ui.lockin_tab import LockInTab
from config.settings import app_settings


class MainWindow(QMainWindow):
    """
    Главное окно приложения
    """

    def __init__(self):
        super().__init__()
        self.magnet_controller = MagnetController()
        self.lockin_controller = LockInController()
        self.hysteresis_measurement = HysteresisMeasurement(  # Создаем экземпляр
            self.magnet_controller,
            self.lockin_controller
        )
        self.data_buffer = DataBuffer()
        self.plot_manager = None

        self.setup_ui()
        self.connect_signals()
        self.load_settings()

    def setup_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Magnet CFU")
        self.setMinimumSize(1000, 700)

        # Создаем центральный виджет и основной layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Создаем разделитель для возможности изменения размера
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель с вкладками
        self.tab_widget = QTabWidget()
        self.control_tab = ControlTab(self.magnet_controller, self.lockin_controller,
                                      self.hysteresis_measurement)  # Передаем hysteresis_measurement
        self.config_tab = ConfigTab(self.magnet_controller)
        self.lockin_tab = LockInTab(self.lockin_controller)

        self.tab_widget.addTab(self.control_tab, "Control")
        self.tab_widget.addTab(self.config_tab, "Config")
        self.tab_widget.addTab(self.lockin_tab, "Lock-in")

        # Правая панель с графиками
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.lockin_plot = LockInPlotWidget()
        self.hysteresis_plot = HysteresisPlotWidget()

        # Добавляем прогресс-бар для измерения гистерезиса
        self.measurement_progress = QProgressBar()
        self.measurement_progress.setVisible(False)

        right_layout.addWidget(self.lockin_plot, 1)
        right_layout.addWidget(self.hysteresis_plot, 1)
        right_layout.addWidget(self.measurement_progress)

        # Создаем менеджер графиков
        self.plot_manager = RealTimePlotManager(self.lockin_plot, self.hysteresis_plot)

        # Добавляем виджеты в разделитель
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])  # начальные размеры

        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        # Настраиваем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Загружаем иконку
        self.setWindowIcon(self.load_icon())

    def load_icon(self):
        """Загрузка иконки приложения"""
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', '01.png')
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def connect_signals(self):
        """Подключение сигналов"""
        # Сигналы от контроллера магнита
        self.magnet_controller.connection_changed.connect(self.on_magnet_connection_changed)
        self.magnet_controller.error_occurred.connect(self.show_error)
        self.magnet_controller.data_received.connect(self.on_magnet_data)

        # Сигналы от контроллера Lock-in
        self.lockin_controller.connected.connect(self.on_lockin_connection_changed)
        self.lockin_controller.error_occurred.connect(self.show_error)
        self.lockin_controller.data_ready.connect(self.on_lockin_data)
        self.lockin_controller.status_update.connect(self.status_label.setText)

        # Сигналы от измерения гистерезиса
        self.hysteresis_measurement.measurement_started.connect(self.on_measurement_started)
        self.hysteresis_measurement.measurement_finished.connect(self.on_measurement_finished)
        self.hysteresis_measurement.measurement_paused.connect(self.on_measurement_paused)
        self.hysteresis_measurement.measurement_resumed.connect(self.on_measurement_resumed)
        self.hysteresis_measurement.data_point_acquired.connect(self.on_data_point_acquired)
        self.hysteresis_measurement.progress_updated.connect(self.on_progress_updated)
        self.hysteresis_measurement.status_message.connect(self.on_status_message)
        self.hysteresis_measurement.error_occurred.connect(self.on_measurement_error)

        # Сигналы от вкладки управления
        self.control_tab.start_measurement.connect(self.start_measurement)
        self.control_tab.stop_measurement.connect(self.stop_measurement)
        self.control_tab.pause_measurement.connect(self.pause_measurement)
        self.control_tab.resume_measurement.connect(self.resume_measurement)
        self.control_tab.clear_plots.connect(self.plot_manager.clear_all)

        # Сигналы от графиков
        self.lockin_plot.point_clicked.connect(self.on_plot_point_clicked)
        self.hysteresis_plot.point_clicked.connect(self.on_plot_point_clicked)

    # ДОБАВЛЯЕМ НЕДОСТАЮЩИЕ МЕТОДЫ ОБРАБОТКИ СИГНАЛОВ

    @pyqtSlot()
    def on_measurement_started(self):
        """Обработчик начала измерения гистерезиса"""
        self.status_label.setText("Измерение гистерезиса запущено")
        self.measurement_progress.setVisible(True)
        self.measurement_progress.setValue(0)
        print("Измерение гистерезиса начато")

    @pyqtSlot()
    def on_measurement_finished(self):
        """Обработчик завершения измерения гистерезиса"""
        self.status_label.setText("Измерение гистерезиса завершено")
        self.measurement_progress.setVisible(False)
        print("Измерение гистерезиса завершено")

    @pyqtSlot()
    def on_measurement_paused(self):
        """Обработчик приостановки измерения"""
        self.status_label.setText("Измерение приостановлено")
        print("Измерение приостановлено")

    @pyqtSlot()
    def on_measurement_resumed(self):
        """Обработчик возобновления измерения"""
        self.status_label.setText("Измерение возобновлено")
        print("Измерение возобновлено")

    @pyqtSlot(dict)
    def on_data_point_acquired(self, data_point):
        """Обработчик получения точки данных"""
        # Обновляем график гистерезиса
        if 'current' in data_point and 'voltage' in data_point:
            # Здесь нужно накопить данные и обновить график
            # Пока просто выводим в консоль
            print(f"Точка данных: ток={data_point['current']:.3f}А, напряжение={data_point['voltage']:.3f}В")

        # Обновляем данные lock-in если они есть
        if 'x' in data_point and 'y' in data_point:
            # Здесь можно обновить график lock-in
            pass

    @pyqtSlot(float)
    def on_progress_updated(self, progress):
        """Обработчик обновления прогресса"""
        self.measurement_progress.setValue(int(progress))
        self.status_label.setText(f"Прогресс измерения: {progress:.1f}%")

    @pyqtSlot(str)
    def on_status_message(self, message):
        """Обработчик сообщений о статусе"""
        self.status_label.setText(message)
        print(f"Статус: {message}")

    @pyqtSlot(str)
    def on_measurement_error(self, error_message):
        """Обработчик ошибок измерения"""
        self.show_error(f"Ошибка измерения: {error_message}")

    # СУЩЕСТВУЮЩИЕ МЕТОДЫ (добавляем к ним)

    def load_settings(self):
        """Загрузка настроек"""
        app_settings.restore_window_geometry(self)

        # Восстанавливаем последние настройки устройств
        last_magnet_port = app_settings.get("serial.default_port")
        if last_magnet_port:
            self.control_tab.set_default_port(last_magnet_port)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Сохраняем настройки
        app_settings.save_window_geometry(self)

        # Останавливаем измерения
        self.stop_measurement()

        # Отключаем устройства
        self.magnet_controller.disconnect()
        self.lockin_controller.disconnect_device()

        event.accept()

    @pyqtSlot(bool)
    def on_magnet_connection_changed(self, connected):
        """Обработка изменения состояния подключения магнита"""
        status = "Connected" if connected else "Disconnected"
        self.status_bar.showMessage(f"Magnet {status}")
        self.control_tab.on_magnet_connection_changed(connected)

    @pyqtSlot(bool)
    def on_lockin_connection_changed(self, connected):
        """Обработка изменения состояния подключения Lock-in"""
        status = "Connected" if connected else "Disconnected"
        self.status_bar.showMessage(f"Lock-in {status}")
        self.lockin_tab.on_lockin_connection_changed(connected)

    @pyqtSlot(str)
    def show_error(self, error_msg):
        """Отображение ошибки"""
        QMessageBox.warning(self, "Error", error_msg)
        self.status_bar.showMessage(f"Error: {error_msg}")

    @pyqtSlot(dict)
    def on_magnet_data(self, data):
        """Обработка данных от магнита"""
        # Обновляем данные на вкладке управления
        self.control_tab.update_measurements(data)

    @pyqtSlot(dict)
    def on_lockin_data(self, data):
        """Обработка данных от Lock-in"""
        # Обновляем график Lock-in
        self.plot_manager.update_lockin_data(data)

        # Передаем данные в измерение гистерезиса
        self.hysteresis_measurement.update_lockin_data(data)

        # Сохраняем данные в буфер
        for channel, channel_data in data.items():
            self.data_buffer.add_data(channel, channel_data['timestamp'], channel_data['value'])

    @pyqtSlot(float, float)
    def on_plot_point_clicked(self, x, y):
        """Обработка клика на графике"""
        self.status_bar.showMessage(f"Point: x={x:.3f}, y={y:.3f}")

    @pyqtSlot(dict)
    def start_measurement(self, parameters):
        """Запуск измерения гистерезиса"""
        try:
            success = self.hysteresis_measurement.start_measurement(parameters)
            if not success:
                self.show_error("Не удалось запустить измерение гистерезиса")
        except Exception as e:
            self.show_error(f"Ошибка запуска измерения: {str(e)}")

    @pyqtSlot()
    def stop_measurement(self):
        """Остановка измерения гистерезиса"""
        try:
            self.hysteresis_measurement.stop_measurement()
        except Exception as e:
            self.show_error(f"Ошибка остановки измерения: {str(e)}")

    @pyqtSlot()
    def pause_measurement(self):
        """Приостановка измерения гистерезиса"""
        try:
            self.hysteresis_measurement.pause_measurement()
        except Exception as e:
            self.show_error(f"Ошибка приостановки измерения: {str(e)}")

    @pyqtSlot()
    def resume_measurement(self):
        """Возобновление измерения гистерезиса"""
        try:
            self.hysteresis_measurement.resume_measurement()
        except Exception as e:
            self.show_error(f"Ошибка возобновления измерения: {str(e)}")
