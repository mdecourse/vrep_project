# -*- coding: utf-8 -*-
import vrep
from math import sqrt, pi
from time import sleep
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from .Ui_VT_v01 import Ui_Form


class init_Form(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(init_Form, self).__init__(parent)
        self.setupUi(self)
        
    ''' 
    def get_pos(clientID, handle):
        return vrep.simxGetObjectPosition(clientID, handle, -1, vrep.simx_opmode_oneshot_wait)
        
    def set_pos(x, y, z, clientID, handle):
        return vrep.simxSetObjectPosition(clientID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)
    '''   
        
    @pyqtSlot()
    def on_print_clicked(self):
        print('OK!!!')
        self.listWidget_results_window.addItem("123test123")
    
    @pyqtSlot()
    def on_with_start_clicked(self):
        dx = self.value_x.value()
        dy = self.value_y.value()
        dz = self.value_z.value()
        d = sqrt(dx * dx + dy * dy + dz * dz)
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
        # 補正後值
        ex = cx + fx
        ey = cy + fy
        ez = cz + fz
        
        vrep.simxFinish(-1)
        clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        for i in range(int(ds)):
            ok, pos = vrep.simxGetObjectPosition(clientID, self.Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
            if ok == vrep.simx_return_ok:
                x, y, z = pos
                self.set_pos(x + tx * step, y + ty * step, z + tz * step, clientID, self.Cub1_handle)

        ok, pos = self.get_pos(clientID, self.Cub1_handle)
        if ok == vrep.simx_return_ok:
            x, y, z = pos
            print('StepMotor_X :', round(cx, 4), 'deg')
            print('StepMotor_Y :', round(cy, 4), 'deg')
            print('StepMotor_Z :', round(cz, 4), 'deg')
            self.set_pos(x + fx, y + fy, z + fz, clientID, self.Cub1_handle)
            self.listWidget_results_window.addItem("(X: {:.04f},Y: {:.04f},Z: {:.04f})".format(ex, ey, ez))
        
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
        vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) # Initialize streaming
        err, Cub1_handle = vrep.simxGetObjectHandle(clientID, "Jet_head_", vrep.simx_opmode_oneshot_wait)
        vrep.simxAddStatusbarMessage(clientID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(clientID)
        vrep.simxFinish(clientID)
