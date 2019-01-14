import sys
from time import sleep
from math import sqrt, pi
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDialog, QApplication
from VT_v01 import Ui_Form
import gcodeParser
import vrep

#from PyQt5.QtGui import *



class readingGcode(QThread):
    def __init__(self,getProgress, layers,  parent=None):
        super(readingGcode, self).__init__(parent)
        self.getProgress = getProgress
        self.layers = layers
        self.mutex = QMutex()
        self.stoped = False
    
    def run(self):
        with QMutexLocker(self.mutex): self.stoped = False
        self.getProgress.setValue(0)
        self.getProgress.setMaximum(len([e for e in self.layers[0].segments]))
        self.layer_vertices = list()
        for layer in self.layers:
            '''
            x = layer.start["X"]
            y = layer.start["Y"]
            z = layer.start["Z"]
            '''
            for seg in layer.segments:
                seg_x = seg.coords["X"]
                seg_y = seg.coords["Y"]
                seg_z = seg.coords["Z"]
                self.layer_vertices.append([seg_x, seg_y, seg_z])
                self.getProgress.setValue(self.getProgress.value()+1)
    
    def stop(self):
        with QMutexLocker(self.mutex): self.stoped = True
        
        
class vrepsetting(QDialog):
    def init_form(self): 
        self.openGcodeFile.clicked.connect(self.__open_file__)
        self.with_start.clicked.connect(self.test)
        self.print.clicked.connect(self.btnstate)
    

    def test(self):
        print(test)
        self.listWidget_results_window.addItem("123test")
        
        
    def hypot_3d(x, y, z):
        return sqrt(x * x + y * y + z * z)
        
    def get_pos(clientID, handle):
        return vrep.simxGetObjectPosition(clientID, handle, -1, vrep.simx_opmode_oneshot_wait)
        
    def set_pos(x, y, z, clientID, handle):
        vrep.simxSetObjectPosition(clientID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)
        
    def walk_to(wx, wy, wz, clientID, handle):
        ok, (ox, oy, oz) = get_pos(clientID, handle)
        walk_with(wx - ox, wy - oy, wz - oz, clientID, handle)
        
    def walk_with(clientID, handle):
        dx = self.value_x.value()
        dy = self.value_y.value()
        dz = self.value_z.value()
        
        d = hypot_3d(dx, dy, dz)
        tx = dx / d
        ty = dy / d
        tz = dz / d
        
        conversion = 1000 / (12 * pi) * 360
        cx = dx * conversion
        cy = dy * conversion
        cz = dz * conversion
        
        step = 0.01
        ds = d // step
        for i in range(int(ds)):
            ok, pos = get_pos(clientID, handle)
            if ok == vrep.simx_return_ok:
                x, y, z = pos
                set_pos(x + tx * step, y + ty * step, z + tz * step, clientID, handle)

        fx = dx % step
        fy = dy % step
        fz = dz % step        
        ok, pos = get_pos(clientID, handle)
        if ok == vrep.simx_return_ok:
            x, y, z = pos
            print('test')
            set_pos(x + fx, y + fy, z + fz, clientID, handle)
            self.listWidget_results_window.addItem("位移量 (X: {:.01f},Y: {:.01f},Z: {:.01f})\n旋轉角 (X: {:.04f},Y: {:.04f},Z: {:.04f})".format(dx, dy, dz, cx, cy, cz))
        
    def m_path(number, clientID, Cub1_handle):
        #每10單位,距離走0.15
        step = 0
        for step_init, step_interval, func in [
            (0, 1, lambda: (0, 0.015 * step, 0.05)),
            (0, 1, lambda: (0.0075 * step, 0.015 * number - 0.01 * step, 0.05)),
            (0, 1, lambda: (0.0075 * number + 0.0075 * step, 0.005 * number + 0.01 * step, 0.05)),
            (number, -1, lambda: (0.015 * number, 0.015 * step, 0.05)),
        ]:
            step = step_init
            for i in range(number):
                step += step_interval
                #returnCode,data=vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_buffer) # Try to retrieve the streamed data
                returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
                if returncode_pos == vrep.simx_return_ok:
                    # After initialization of streaming, it will take a few ms before the first value arrives, so check the return code
                    x, y, z = data_pos
                    vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, func(), vrep.simx_opmode_oneshot_wait)
        
    def main():
        vrep.simxFinish(-1)
        clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if clientID == -1:
            print ('Failed connecting to remote API server')
            return

        print ('Connected to remote API server')
        # Now try to retrieve data in a blocking fashion (i.e. a service call):
        res, objs = vrep.simxGetObjects(clientID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print ('Number of objects in the scene:', len(objs))
        else:
            print ('Remote API function call returned with error code:', res)

        sleep(2) 
        # Now retrieve streaming data (i.e. in a non-blocking fashion):
        vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) # Initialize streaming
        err, Cub1_handle = vrep.simxGetObjectHandle(clientID, "Cub1", vrep.simx_opmode_oneshot_wait)
        err, nozzle_handle = vrep.simxGetObjectHandle(clientID, "nozzle", vrep.simx_opmode_oneshot_wait)
        
        # M path
        # m_path(30, clientID, Cub1_handle)
        #walk_to(0, 0, 0.5, clientID, Cub1_handle)
        # walk_with(1, 0, 0, clientID, Cub1_handle)
        #walk_with(-0.3, -0.5, 0, clientID, Cub1_handle)
        walk_with(-0.3, -0.3, 0, clientID, Cub1_handle)
        walk_with(0.3, 0.3, 0, clientID, Cub1_handle)

        # Now send some data to V-REP in a non-blocking fashion:
        vrep.simxAddStatusbarMessage(clientID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
        vrep.simxGetPingTime(clientID)
        # Now close the connection to V-REP:
        vrep.simxFinish(clientID)
        
    def __open_file__(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Files", '..', 'GCode(*.gcode)')
        if filename:
            
            #path = 'test_gcode.gcode'
            parser = GcodeParser()
            self.model = parser.parseFile(filename)
            print("Done! %s"%self.model)
            
            self.renderVertices()
            get = []
            for i in range(len(self.layer_vertices)):
                x, y, z = self.parsePostion(i)
                get = str(x),str(y), str(z)
                self.gcodeList.addItem(str(get) )
                self.sendPoisiontoVrep(x, y, z)
                #print(x, y, z)
        else:
            print("No file")
            
        
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
    vt = vrepsetting()
    vt.show()
    sys.exit(app.exec_())