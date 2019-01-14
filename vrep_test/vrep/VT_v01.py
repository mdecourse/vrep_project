# -*- coding: utf-8 -*-
from . import vrep
from math import sqrt, pi
from time import sleep
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from .Ui_VT_v01 import Ui_Form


class init_Form(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(init_Form, self).__init__(parent)
        self.setupUi(self)
        self.init_Forms()
        self.clientID = None
        
    def init_Forms(self):
        self.print.clicked.connect(self.print_go)
        self.with_start.clicked.connect(self.with_go)
        
    '''
     def get_pos(clientID, handle):
         return vrep.simxGetObjectPosition(clientID, handle, -1, vrep.simx_opmode_oneshot_wait)
    def set_pos(x, y, z, clientID, handle):
        return vrep.simxSetObjectPosition(clientID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)
    '''
    
    #@pyqtSlot()
    def print_go(self):
        print('OK!!!')
        self.listWidget_results_window.addItem("123test123")
        
    @pyqtSlot()
    def with_go(self):
        handle,  handle_value = vrep.simxGetObjectHandle(self.clientID, "cupid", vrep.simx_opmode_oneshot_wait)
        dx = self.value_x.value()
        dy = self.value_y.value()
        dz = self.value_z.value()
        #self.value_3d(self, dx,  dy,  dz)
        d = sqrt(dx * dx + dy * dy + dz * dz)
        
        if d != 0:
            # 移動量
            tx = dx / d
            ty = dy / d
            tz = dz / d
            
        # EX. 馬達脈波:  移動量(mm) / 馬達單圈移動量(mm) x 360(deg) / 步數(step)
        # EX. conversion = 1000 / (12 * pi) * (360 / 200)
        conversion = 1000 / (12 * pi) * 360
        cx = dx * conversion
        cy = dy * conversion
        cz = dz * conversion
        # EX. 單步移動量step = 12 * 0.001 * pi / 200(step)
        step = 0.01
        ds = d // step
        # 補正誤差值
        fx = dx % step
        fy = dy % step
        fz = dz % step

        for i in range(int(ds)):
            ok, pos = vrep.simxGetObjectPosition(self.clientID, handle_value, -1, vrep.simx_opmode_oneshot_wait)
            if ok == vrep.simx_return_ok:
                x, y, z = pos
                vrep.simxSetObjectPosition(self.clientID, handle_value, -1, (x + tx * step, y + ty * step, z + tz * step), vrep.simx_opmode_oneshot_wait)
                # self.set_pos(x + tx * step, y + ty * step, z + tz * step, self.clientID, handle)
        ok, pos  = vrep.simxGetObjectPosition(self.clientID, handle_value, -1, vrep.simx_opmode_oneshot_wait)
        print(pos)
        if ok == vrep.simx_return_ok:
            x, y, z = pos
            print('StepMotor_X :', round(cx, 4), 'deg')
            print('StepMotor_Y :', round(cy, 4), 'deg')
            print('StepMotor_Z :', round(cz, 4), 'deg')
            vrep.simxSetObjectPosition(self.clientID, handle_value, -1, (x + fx, y + fy, z + fz), vrep.simx_opmode_oneshot_wait)
            self.listWidget_results_window.addItem("(X: {:.04f},Y: {:.04f},Z: {:.04f})".format(x+fx, y+fy, z+fz))
        
    def main():
        vrep.simxFinish(-1)
        clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if clientID == -1:
            print ('Failed connecting to remote API server')
            return
            
        print ('Connected to remote API server')
        res, objs = vrep.simxGetObjects(clientID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print ('Number of objects in the scene:', len(objs))
        else:
            print ('Remote API function call returned with error code:', res)

        sleep(2) 
        vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) 
        #err, Jet_handle = vrep.simxGetObjectHandle(clientID, "Jet_head_", vrep.simx_opmode_oneshot_wait)
        vrep.simxGetObjectHandle(clientID, "Jet_head_", vrep.simx_opmode_oneshot_wait)
        vrep.simxAddStatusbarMessage(clientID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(clientID)
        vrep.simxFinish(clientID)
    
    @pyqtSlot()
    def on_str_rdbtn_clicked(self):
        vrep.simxFinish(-1)
        self.clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if self.clientID == -1:
            print ('Failed connecting to remote API server')
            return
        print ('Connected to remote API server')
        res, objs = vrep.simxGetObjects(self.clientID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print ('Number of objects in the scene:', len(objs))
        else:
            print ('Remote API function call returned with error code:', res)
        vrep.simxGetIntegerParameter(self.clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) # Initialize streaming
        vrep.simxAddStatusbarMessage(self.clientID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(self.clientID)
    
    @pyqtSlot()
    def on_stop_rdbtn_clicked(self):
        vrep.simxFinish(self.clientID)
