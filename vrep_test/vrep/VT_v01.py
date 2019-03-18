# -*- coding: utf-8 -*-

from typing import Tuple
from math import sqrt
from threading import Thread
from PyQt5.QtCore import pyqtSlot, QThread, QMutexLocker
from PyQt5.QtWidgets import *
from . import vrep
from .Ui_VT_v01 import Ui_Dialog
from .gcodeParser import *

#client_ID = -1

def _no_error(func):
    def check_func(*args):
        r = func(*args)
        if type(r) == tuple:
            return r[1]
        else:
            return None
    return check_func

@_no_error
def get_pos(handle: object) -> Tuple[float, float, float]:
    """Get position from V-rep."""
    return vrep.simxGetObjectPosition(client_ID, handle, -1, vrep.simx_opmode_oneshot_wait)

@_no_error
def set_pos(x: float, y: float, z: float, handle: object) -> None:
    return vrep.simxSetObjectPosition(client_ID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)


class readingGcode(QThread):
    def __init__(self, getProgress, layers, parent=None):
        super(readingGcode, self).__init__(parent)
        self.getProgress = getProgress
        self.layers = layers
        self.mutex = QMutex()
        self.stoped = False

    def run(self):
        with QMutexLocker(self.mutex):
            self.stoped = False
        self.getProgress.setValue(0)
        self.getProgress.setMaximum(len([e for e in self.layers[0].segments]))
        self.layer_vertices = list()
        for layer in self.layers:
            for seg in layer.segments:
                seg_x = seg.coords["X"]
                seg_y = seg.coords["Y"]
                seg_z = seg.coords["Z"]
                self.layer_vertices.append([seg_x, seg_y, seg_z])
                self.getProgress.setValue(self.getProgress.value() + 1)

    def stop(self):
        with QMutexLocker(self.mutex): 
            self.stoped = True


class ControlPanel(QDialog, Ui_Dialog):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.setupUi(self)
        self.main()
        
    '''
    @pyqtSlot(name='on_print_clicked')
    def print_go(self):
        print('[INFO] print object OK!!!')
        self.listWidget_results_window.addItem(f'[INFO] Select object: {self.lineEdit.text()}')
    '''
    
    #試寫A.B物件復歸
    @pyqtSlot(name='on_print_clicked')
    def print_movehere(self):
        dm = 0.001
        step = 0.005
        no_, handle_designation = vrep.simxGetObjectHandle(client_ID, self.lineEdit.text(), vrep.simx_opmode_oneshot_wait)
        no_, handle_reference = vrep.simxGetObjectHandle(client_ID, 'box0', vrep.simx_opmode_oneshot_wait)
        x1, y1, z1 = get_pos(handle_designation)
        x2, y2, z2 = get_pos(handle_reference)
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            if d == 0:
                return self.listWidget_results_window.addItem('[INFO] Have arrived at the destination')
            ds = d // step                 
            # 移動量
            tx = dx / ds
            ty = dy / ds
            tz = dz / ds
            for _ in range(int(ds)):
                x, y, z = get_pos(handle_designation)
                set_pos(x + tx, y + ty, z + tz, handle_designation)
            x, y, z = get_pos(handle_designation)
            self.listWidget_results_window.addItem(f"[INFO] X: {x/dm:.01f}, Y: {y/dm:.01f}, Z: {z/dm:.01f}")
        thread = Thread(target=do, args=(x2 - x1, y2 - y1, z2 - z1))
        thread.start()
        
    @pyqtSlot(name='on_with_start_clicked')
    def with_go(self):
        dm = 0.001
        step = 0.005
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            if d == 0:
                return self.listWidget_results_window.addItem('[WARN] Please set value!!')
            elif d < step:
                return self.listWidget_results_window.addItem('[WARN] The value is too small!!')
            handle, handle_value = vrep.simxGetObjectHandle(client_ID, self.lineEdit.text(), vrep.simx_opmode_oneshot_wait)
            ds = d // step
            # 移動量
            tx = dx / ds
            ty = dy / ds
            tz = dz / ds
            # EX. 馬達脈波:  移動量(mm) / 馬達單圈移動量(mm) x 360(deg) / 步數(step)
            cx = dx * 90
            cy = dy * 90
            cz = dz * 90
            for _ in range(int(ds)):
                x, y, z = get_pos(handle_value)
                set_pos(x + tx, y + ty, z + tz, handle_value)
            x, y, z = get_pos(handle_value)
            print(f'[INFO] StepMotor_X: {cx:.01f} deg')
            print(f'[INFO] StepMotor_Y: {cy:.01f} deg')
            print(f'[INFO] StepMotor_Z: {cz:.01f} deg')
            self.listWidget_results_window.addItem(f"[INFO] X: {x/dm:.01f}, Y: {y/dm:.01f}, Z: {z/dm:.01f}")
        thread = Thread(target=do, args=(self.value_x.value() * dm, self.value_y.value() * dm, self.value_z.value() * dm))
        thread.start()

    @pyqtSlot(name='on_with_open_clicked')
    def __open_file__(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Files", 'gcode', 'GCode(*.gcode)')  #title,path,filename
        if filename:
            parser = GcodeParser()
            self.model = parser.parseFile(filename)
            print("Done! %s" % self.model)

            self.renderVertices()
            get = []
            for i in range(len(self.layer_vertices)):
                x, y, z = self.parsePostion(i)
                get = str(x), str(y), str(z)
                self.listWidget_results_window.addItem(str(get))
                self.sendPoisiontoVrep(x, y, z)
                # print(x, y, z)
        else:
            print("No file")

    def sendPoisiontoVrep(self, e, r, t):

        vrep.simxFinish(-1)
        clientID = vrep.simxStart('127.0.0.1', 19998, True, True, 5000, 5)
        if clientID!= -1:
            time.sleep(0.5)
            errorCode,plate=vrep.simxGetObjectHandle(clientID,'plate',vrep.simx_opmode_oneshot_wait)


            if errorCode == -1:
                sys.exit()
            errorCode=vrep.simxSetObjectPosition(clientID,plate,-1,
                                                 [e/1000,r/1000,t/1000+0.1165],
                                                 vrep.simx_opmode_oneshot_wait
            )
        else:
            print('Connection not successful')
            sys.exit('Could not connect')

    def renderVertices(self):
        work = readingGcode(self.progressBar, self.model.layers)
        work.run()
        self.layer_vertices = work.layer_vertices

    def parsePostion(self, pos):
        row = self.layer_vertices[pos]
        return row[0], row[1], row[2]

    def main(self):
        vrep.simxFinish(-1)
        global client_ID
        client_ID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if client_ID == -1:
            print('Failed connecting to remote API server')
            return
        print('Connected to remote API server')
        res, objs = vrep.simxGetObjects(client_ID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print(f'Number of objects in the scene: {len(objs)}')
        else:
            print(f'Remote API function call returned with error code: {res}')
        # Initialize streaming
        vrep.simxGetIntegerParameter(client_ID, vrep.sim_intparam_mouse_x, vrep.simx_opmode_streaming)
        vrep.simxAddStatusbarMessage(client_ID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(client_ID)
