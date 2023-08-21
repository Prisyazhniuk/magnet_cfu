from PyQt6.QtWidgets import QApplication, QLabel, QLayout, QPushButton, QWidget, QVBoxLayout
# from PyQtб import QtWidgets
import sys
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Пepвaя программа на PyQt")
window.resize(300, 70)
label = QLabel("<center>Пpивeт, миp!</center>")
btnQuit = QPushButton ( "&Закрыть окно")
vbox = QVBoxLayout()
vbox.addWidget(label)
vbox.addWidget(btnQuit)
window.setLayout(vbox)
btnQuit.clicked.connect(app.quit)
window.show()
app.exec()