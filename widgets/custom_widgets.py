from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QDoubleSpinBox, QSpinBox, QComboBox, QPushButton)
from PyQt5.QtCore import pyqtSignal


class LabeledSpinBox(QWidget):
    """Виджет с меткой и спинбоксом"""
    valueChanged = pyqtSignal(float)

    def __init__(self, label, min_val, max_val, step, decimals=2, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setSingleStep(step)
        self.spinbox.setDecimals(decimals)

        layout.addWidget(self.label)
        layout.addWidget(self.spinbox)

        self.spinbox.valueChanged.connect(self.valueChanged)

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value)


class LabeledComboBox(QWidget):
    """Виджет с меткой и комбобоксом"""
    currentTextChanged = pyqtSignal(str)

    def __init__(self, label, items, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.combobox = QComboBox()
        self.combobox.addItems(items)

        layout.addWidget(self.label)
        layout.addWidget(self.combobox)

        self.combobox.currentTextChanged.connect(self.currentTextChanged)

    def currentText(self):
        return self.combobox.currentText()

    def setCurrentText(self, text):
        self.combobox.setCurrentText(text)


class ToggleButton(QPushButton):
    """Кнопка-переключатель с двумя состояниями"""

    def __init__(self, on_text, off_text, parent=None):
        super().__init__(off_text, parent)
        self.on_text = on_text
        self.off_text = off_text
        self.is_on = False
        self.clicked.connect(self.toggle)

    def toggle(self):
        self.is_on = not self.is_on
        self.setText(self.on_text if self.is_on else self.off_text)

    def setState(self, state):
        self.is_on = state
        self.setText(self.on_text if self.is_on else self.off_text)