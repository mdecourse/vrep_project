# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from .Ui_VT_v01 import Ui_Form


class init_Form(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(init_Form, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_print_clicked(self):
        print('OK!!!')
