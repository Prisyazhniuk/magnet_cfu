import json
import os
from pathlib import Path
from typing import Dict, Any
from PyQt5.QtCore import QByteArray


class Settings:
    """Класс для управления настройками приложения"""

    def __init__(self):
        self.config_dir = Path.home() / ".magnet_cfu_v2"
        self.config_file = self.config_dir / "settings.json"
        self.default_settings = {
            "serial": {
                "default_port": "COM9",
                "baud_rate": 115200,
                "data_bits": 8,
                "parity": "No Parity",
                "stop_bits": "One Stop",
                "flow_control": "No Flow Control",
                "timeout": 1
            },
            "lockin": {
                "device_id": "dev4999",
                "host": "localhost",
                "port": 8004,
                "api_level": 6
            },
            "measurement": {
                "default_current_range": [-7.5, 7.5],
                "default_step": 0.01,
                "default_interval": 1000,
                "max_loops": 10
            },
            "ui": {
                "window_size": [1200, 800],
                "plot_history_size": 1000,
                "plot_time_window": 10
            }
        }
        self._ensure_config_dir()
        self.settings = self._load_settings()

    def _ensure_config_dir(self):
        """Создает директорию для конфигурационных файлов"""
        self.config_dir.mkdir(exist_ok=True)

    def _load_settings(self) -> Dict[str, Any]:
        """Загружает настройки из файла или создает default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки настроек: {e}. Использую настройки по умолчанию.")

        # Сохраняем настройки по умолчанию
        self._save_settings(self.default_settings)
        return self.default_settings.copy()

    def _save_settings(self, settings: Dict[str, Any]):
        """Сохраняет настройки в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get(self, key: str, default=None):
        """Получает значение настройки по ключу (dot notation)"""
        keys = key.split('.')
        value = self.settings

        try:
            for k in keys:
                value = value[k]

            # Проверяем и исправляем проблемные значения
            if key == "serial.parity" and isinstance(value, int):
                parity_options = ['No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity']
                if 0 <= value < len(parity_options):
                    corrected_value = parity_options[value]
                    self.set(key, corrected_value)  # Автоисправление
                    return corrected_value

            if key == "serial.stop_bits" and isinstance(value, int):
                stopbits_options = ['One Stop', 'One And Half Stop', 'Two Stop']
                if 0 <= value < len(stopbits_options):
                    corrected_value = stopbits_options[value]
                    self.set(key, corrected_value)  # Автоисправление
                    return corrected_value

            if key == "serial.flow_control" and isinstance(value, int):
                flowcontrol_options = ['No Flow Control', 'Hardware Control', 'Software Control']
                if 0 <= value < len(flowcontrol_options):
                    corrected_value = flowcontrol_options[value]
                    self.set(key, corrected_value)  # Автоисправление
                    return corrected_value

            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value):
        """Устанавливает значение настройки"""
        keys = key.split('.')
        settings_ref = self.settings

        # Проходим по всем ключам кроме последнего
        for k in keys[:-1]:
            if k not in settings_ref:
                settings_ref[k] = {}
            settings_ref = settings_ref[k]

        # Устанавливаем значение
        settings_ref[keys[-1]] = value
        self._save_settings(self.settings)

    def save_window_geometry(self, window):
        """Сохраняет геометрию окна"""
        geometry = window.saveGeometry()
        # Исправлено: правильное преобразование QByteArray в строку
        geometry_data = geometry.toBase64().data().decode('utf-8')
        self.set("ui.window_geometry", geometry_data)

    def restore_window_geometry(self, window):
        """Восстанавливает геометрию окна"""
        geometry_data = self.get("ui.window_geometry")
        if geometry_data:
            from PyQt5.QtCore import QByteArray
            # Исправлено: правильное преобразование строки в QByteArray
            window.restoreGeometry(QByteArray.fromBase64(geometry_data.encode('utf-8')))


# Глобальный экземпляр настроек
app_settings = Settings()
