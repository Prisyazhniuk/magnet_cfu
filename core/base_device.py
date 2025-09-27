# core/base_device.py
from abc import ABC, abstractmethod
from PyQt5.QtCore import QObject, pyqtSignal


class BaseDeviceController(QObject):
    connected = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    data_ready = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_connected = False

    @abstractmethod
    def connect_device(self):
        pass

    @abstractmethod
    def disconnect_device(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass