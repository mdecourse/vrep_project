from vrep.VT_v01 import init_Form
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__' :
    app = QApplication([])
    run = init_Form()
    run.show()
    exit(app.exec_())
