import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg


app = QApplication(sys.argv)


plt = pg.plot()
plt.setWindowTitle('GeeksCoders.com - Legends Example')
plt.addLegend()

c1 = plt.plot([1,3,2,4], pen='y', name='Yellow Plot')
c2 = plt.plot([2,1,4,3], pen='b', fillLevel=0, fillBrush=(255,255,255,30), name='Blue Plot')
c3 = plt.addLine(y=4, pen='y')

status = app.exec_()
sys.exit(status)