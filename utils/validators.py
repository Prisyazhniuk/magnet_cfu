from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp


class NumberValidator(QDoubleValidator):
    """Валидатор для числовых значений с улучшенной обработкой"""

    def __init__(self, bottom, top, decimals=2, parent=None):
        super().__init__(bottom, top, decimals, parent)
        self.setNotation(QDoubleValidator.StandardNotation)

    def validate(self, input_str, pos):
        """Переопределение валидации для лучшей обработки пустых строк"""
        result = super().validate(input_str, pos)

        # Разрешаем пустую строку во время ввода
        if input_str == "":
            return (QDoubleValidator.Intermediate, input_str, pos)

        return result

    def fixup(self, input_str):
        """Исправление ввода при невалидных данных"""
        if not input_str:
            return "0"
        try:
            value = float(input_str)
            # Ограничиваем значение допустимыми пределами
            value = max(self.bottom(), min(self.top(), value))
            return f"{value:.{self.decimals()}f}"
        except ValueError:
            return f"{self.bottom():.{self.decimals()}f}"


class PortValidator(QRegExpValidator):
    """Валидатор для COM-портов"""

    def __init__(self, parent=None):
        # Регулярное выражение для COM-портов (COM1-COM99)
        regex = QRegExp("^COM[1-9][0-9]?$")
        super().__init__(regex, parent)


class IPValidator(QRegExpValidator):
    """Валидатор для IP-адресов"""

    def __init__(self, parent=None):
        regex = QRegExp("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        super().__init__(regex, parent)


class ScientificValidator(QDoubleValidator):
    """Валидатор для научной нотации"""

    def __init__(self, parent=None):
        super().__init__()
        self.setNotation(QDoubleValidator.ScientificNotation)

    def validate(self, input_str, pos):
        # Базовая валидация
        result = super().validate(input_str, pos)

        # Дополнительная проверка для научной нотации
        if input_str and 'e' in input_str.lower():
            parts = input_str.lower().split('e')
            if len(parts) != 2:
                return (QDoubleValidator.Invalid, input_str, pos)

        return result