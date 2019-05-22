# -*- coding: utf-8 -*-
from typing import Tuple
from math import sqrt
from threading import Thread
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from . import vrep
from .Ui_VT_v01 import Ui_Daci
import re
import time
WAIT = vrep.simx_opmode_oneshot_wait # V-REP data transmission modes

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
    return vrep.simxGetObjectPosition(client_ID, handle, -1, WAIT)

@_no_error
def set_pos(x: float, y: float, z: float, handle: object) -> None:
    return vrep.simxSetObjectPosition(client_ID, handle, -1, (x, y, z), WAIT)


class ControlPanel(QDialog, Ui_Daci):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.setupUi(self)
        self.main()
        
    @pyqtSlot(name='on_click_x_up_clicked')
    def xaxis(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx + 0.001, my, mz, handle_name1)
       
    @pyqtSlot(name='on_click_x_down_clicked')
    def xaxis_(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx - 0.001, my, mz, handle_name1)
        
    @pyqtSlot(name='on_click_y_up_clicked')
    def yaxis(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx, my + 0.001, mz, handle_name1)
        
    @pyqtSlot(name='on_click_y_down_clicked')
    def yaxis_(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx, my - 0.001, mz, handle_name1)
        
    @pyqtSlot(name='on_click_z_up_clicked')
    def zaxis(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx, my, mz + 0.001, handle_name1)
        
    @pyqtSlot(name='on_click_z_down_clicked')
    def zaxis_(self):
        no_, handle_name1 = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        mx, my, mz = get_pos(handle_name1)
        set_pos(mx, my, mz - 0.001, handle_name1)
        
    @pyqtSlot(name='on_click_return_clicked') 
    def _return_(self):  # 原點復歸
        dm = 0.001
        step = 0.005
        no_, handle_designation = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
        no_, handle_reference = vrep.simxGetObjectHandle(client_ID, 'box0', WAIT)
        x1, y1, z1 = get_pos(handle_designation)
        x2, y2, z2 = get_pos(handle_reference)
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            ds = d // step
            if d == 0 or ds == 0:
                return self.print_output.addItem('[INFO] Have arrived at the destination')
            tx = dx / ds # 移動量
            ty = dy / ds
            tz = dz / ds
            for _ in range(int(ds)):
                x, y, z = get_pos(handle_designation)
                set_pos(x + tx, y + ty, z + tz, handle_designation)
            x, y, z = get_pos(handle_designation)
            self.print_output.addItem(f"[INFO] X: {x/dm:.01f}, Y: {y/dm:.01f}, Z: {z/dm:.01f}")
        thread = Thread(target=do, args=(x2 - x1, y2 - y1, z2 - z1))
        thread.start()

    #@pyqtSlot(name='on_click_start2_clicked')
    def gcode_return_(self):  # 分割式原點復歸 XY/Z
        no_, handle_Hnow = vrep.simxGetObjectHandle(client_ID, self.edit_name2.text(), WAIT)
        no_, handle_Vnow = vrep.simxGetObjectHandle(client_ID, self.edit_name3.text(), WAIT)
        no_, handle_reference = vrep.simxGetObjectHandle(client_ID, 'box0', WAIT)
        x1, y1, z1 = get_pos(handle_Hnow)
        x2, y2, z2 = get_pos(handle_Vnow)
        x3, y3, z3 = get_pos(handle_reference)
        z3 = z3 - 0.13 # 平台與原點之最小距離
        step = 0.005
        def do(dx, dy, dz):
            dh = sqrt(dx * dx + dy * dy)
            dhs = dh // step
            dvs = dz // step
            if dh == 0 or dhs == 0:
                self.print_output.addItem('[INFO] G28 X0. Y0.')
                time.sleep(0.5)
            else:
                tx = dx / abs(dhs)
                ty = dy / abs(dhs)
                for m in range(int(abs(dhs))):
                    x1, y1, z1 = get_pos(handle_Hnow)
                    set_pos(x1 + tx, y1 + ty, z1, handle_Hnow)
                self.print_output.addItem('[INFO] G28 X0. Y0.')
                time.sleep(0.5)
            if dz == 0 or dvs == 0:
                self.print_output.addItem('[INFO] G28 Z0.')
                time.sleep(0.5)
            else:
                tz = dz / abs(dvs)
                for n in range(int(abs(dvs))):
                    x2, y2, z2 = get_pos(handle_Vnow)
                    set_pos(x2, y2, z2 - tz, handle_Vnow)
                self.print_output.addItem('[INFO] G28 Z0.')
                time.sleep(0.5)
        thread = Thread(target=do, args=(x3 - x1, y3 - y1, z2 - z3))
        thread.start()
    

    @pyqtSlot(name='on_click_start1_clicked')
    def with_go(self):  # 手動控制
        dm = 0.001
        step = 0.005
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            if d == 0:
                return self.print_output.addItem('[WARN] Please set value!!')
            elif d < step:
                return self.print_output.addItem('[WARN] The value is too small!!')
            handle, handle_value = vrep.simxGetObjectHandle(client_ID, self.edit_name1.text(), WAIT)
            ds = d // step
            tx = dx / ds # 移動量
            ty = dy / ds
            tz = dz / ds
            for _ in range(int(ds)):
                x, y, z = get_pos(handle_value)
                set_pos(x + tx, y + ty, z + tz, handle_value)
            x, y, z = get_pos(handle_value)
            self.print_output.addItem(f"[INFO] X: {x/dm:.01f}, Y: {y/dm:.01f}, Z: {z/dm:.01f}")
        thread = Thread(target=do, args=(self.value_x.value() * dm, self.value_y.value() * dm, self.value_z.value() * dm))
        thread.start()
    
    @pyqtSlot(name='on_click_start2_clicked')
    def open_go(self):
        print(self.gcode_return_())
        time.sleep(8)
        no_, handle_Hnow = vrep.simxGetObjectHandle(client_ID, self.edit_name2.text(), WAIT)
        no_, handle_Vnow = vrep.simxGetObjectHandle(client_ID, self.edit_name3.text(), WAIT)
        no_, handle_reference = vrep.simxGetObjectHandle(client_ID, 'box0', WAIT)
        x1, y1, z1 = get_pos(handle_Hnow)
        x2, y2, z2 = get_pos(handle_Vnow)
        x3, y3, z3 = get_pos(handle_reference)
        z3 = z3 - 0.13 # 平台與原點之最小距離
        step = 0.005
        dm = 0.001
        f = open('vrep/gcode.txt', 'r')
        for line in f.readlines(): 
            line = line.split(',') 
            x = float(line[0]) * dm
            y = float(line[1]) * dm
            z = float(line[2]) * dm
            dx = x - (x1 - x3)
            dy = y - (y1 - y3)
            dh = sqrt(dx * dx + dy * dy)
            dhs = dh // step
            self.print_output.addItem(f"[INFO] X: {x/dm:.03f} Y: {y/dm:.03f} Z: {z/dm:.03f}")
            #time.sleep(0.5)
            if dhs <= 0:
                x1, y1, z1 = get_pos(handle_Hnow)
                set_pos(x1 + dx, y1 + dy, z1, handle_Hnow)
            else:
                tx = dx / abs(dhs)
                ty = dy / abs(dhs)
                for m in range(abs(int(dhs))):
                    x1, y1, z1 = get_pos(handle_Hnow)
                    set_pos(x1 + tx, y1 + ty, z1, handle_Hnow)
                    #if x1 == x3 and y1 == y3:
                        #self.print_output.addItem('[INFO] G28 X0. Y0.')
            #time.sleep(1000)
        f.close()
        print(self.gcode_return_())   
        
    @pyqtSlot(name='on_click_open_clicked')
    def __open_file__(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Files", 'gcode', 'GCode(*.gcode)')  #title,path,filename
        DEFAULT_NC_SYNTAX = ("(?:G([0-9]?\d+\.?\d*))?(?:M([+-]?\d+\.?\d*))?(?:\sF([+-]?\d+\.?\d*))?(?:\sS([+-]?\d+\.?\d*))?(?:\sX([+-]?\d+\.?\d*))?(?:\sY([+-]?\d+\.?\d*))?(?:\sZ([+-]?\d+\.?\d*))?(?:\sE([+-]?\d+\.?\d*))?(?:\sX([+-]?\d+\.?\d*))?(?:\sY([+-]?\d+\.?\d*))?(?:\sF([+-]?\d+\.?\d*))?(?:\sZ([+-]?\d+\.?\d*))?(?:\ +|\w+|\,\w+)?(?:,?\ \w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?)?(?:;\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?\w+\ ?)?(?:[(]\w+\ \w+\ \w+\ \w+\))?(?:;\w+\ ?\w+)?")
        with open(filename, 'r', encoding='utf-8') as g:
            gcord = g.read()
        f = open('vrep/gcode.txt', 'w+')
        def _match(patten, doc):
            yield from re.compile(patten, re.MULTILINE).finditer(doc)
        
        for m in _match(DEFAULT_NC_SYNTAX, gcord):
            mx = m.group(5)
            my = m.group(6)
            mz = m.group(7)
            if mx is None and my is None and mz is None:
                None
            elif mx is None and my is None and mz is not None:
                mx = 0.0
                my = 0.0
                f.write(str(mx) + ', ' + str(my) + ', ' + str(mz) + ',' + '\n')
            elif mx is not None and my is not None and mz is None:
                mz = 0.0
                f.write(str(mx) + ', ' + str(my) + ', ' + str(mz) + ',' + '\n')
            elif mx is not None and my is None and mz is None:
                None
            else:
                f.write(str(mx) + ', ' + str(my) + ', ' + str(mz) + ',' + '\n')
        f.close()
        self.print_output.addItem(f"[INFO] The file has been successfully read.")
            
    def main(self):
        vrep.simxFinish(-1)
        global client_ID
        client_ID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if client_ID == -1:
            print('[WARN] Failed connecting to remote API server')
            return
        print('[INFO] Connected to remote API server')
        res, objs = vrep.simxGetObjects(client_ID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print(f'[INFO] Number of objects in the scene: {len(objs)}')
        else:
            print(f'[WARN] Remote API function call returned with error code: {res}')
        vrep.simxGetIntegerParameter(client_ID, vrep.sim_intparam_mouse_x, vrep.simx_opmode_streaming)
        vrep.simxAddStatusbarMessage(client_ID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(client_ID)
