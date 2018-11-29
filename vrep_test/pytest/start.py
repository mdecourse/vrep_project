import sys
from PyQt5.QtWidgets import QDialog, QApplication
from VT_v01 import Ui_Form

class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.show()
        
    def setupUi(self):
        setWindowTitle(_translate("Form", "Form"))
    
    def pushButton_Click(self):
        self.ui.pushButton.setText("Hello World")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())