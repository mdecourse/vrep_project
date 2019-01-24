# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Y:\tmp\vrep_project\vrep_test\arduino\pyquino.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(401, 302)
        self.test_listWidget = QtWidgets.QListWidget(Dialog)
        self.test_listWidget.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.test_listWidget.setObjectName("test_listWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

