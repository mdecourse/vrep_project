# -*- coding: utf-8 -*-

from vrep.VT_v01 import ControlPanel
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication([])
    run = ControlPanel()
    run.show()
    exit(app.exec_())
