import os

os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'

import sys
from PyQt5.QtWidgets import QApplication


def main():
    # Простой тест без сложных импортов
    try:
        app = QApplication(sys.argv)

        # Проверяем основные импорты
        import pyqtgraph as pg
        print("PyQtGraph imported successfully")

        from core.magnet_controller import MagnetController
        print("MagnetController imported successfully")

        from core.lockin_controller import LockInController
        print("LockInController imported successfully")

        from ui.main_window import MainWindow
        print("MainWindow imported successfully")

        # Если все импорты прошли успешно, запускаем приложение
        window = MainWindow()
        window.show()

        print("Application started successfully!")
        return app.exec()

    except ImportError as e:
        print(f"Import error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())



# import os
#
# os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'  # Принудительно используем PyQt5
#
# import sys
# import pyqtgraph as pg
# from PyQt5.QtWidgets import QApplication
# from ui.main_window import MainWindow
#
#
# def load_stylesheet():
#     """Загрузка стилей приложения"""
#     try:
#         with open('styles.qss', 'r', encoding='utf-8') as file:
#             return file.read()
#     except FileNotFoundError:
#         print("Файл стилей не найден. Используются стандартные стили.")
#         return ""
#
#
# if __name__ == "__main__":
#     # Явно создаем QApplication вместо pg.mkQApp()
#     app = QApplication(sys.argv)
#
#     # Загрузка стилей
#     app.setStyleSheet(load_stylesheet())
#
#     # Создание и отображение главного окна
#     window = MainWindow()
#     window.show()
#
#     sys.exit(app.exec())