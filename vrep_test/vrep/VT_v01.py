# -*- coding: utf-8 -*-

from typing import Tuple
from math import sqrt, pi
from threading import Thread
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QDialog
from . import vrep
from .Ui_VT_v01 import Ui_Dialog

#client_ID = -1

def _no_error(func):
    def check_func(*args):
        r = func(*args)
        if type(r) == tuple:
            if r[0] != vrep.simx_return_ok:
                raise ValueError("not ok")
            return r[1]
        else:
            if r != vrep.simx_return_ok:
                raise ValueError("not ok")
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
        with QMutexLocker(self.mutex): self.stoped = True

class ControlPanel(QDialog, Ui_Dialog):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.setupUi(self)
        self.main()

    @pyqtSlot(name='on_print_clicked')
    def print_go(self):
        print('[INFO] print object OK!!!')
        self.listWidget_results_window.addItem(f'[INFO] Select object: {self.lineEdit.text()}')

    @pyqtSlot(name='on_with_start_clicked')
    def with_go(self):
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            if d == 0:
                return self.listWidget_results_window.addItem('[WARN] Please set value!!')
            handle, handle_value = vrep.simxGetObjectHandle(client_ID,
                                                            self.lineEdit.text(),
                                                            vrep.simx_opmode_oneshot_wait
                                                            )
            step = 0.01
            ds = d // step
            # 移動量
            tx = dx / ds
            ty = dy / ds
            tz = dz / ds
            # EX. 馬達脈波:  移動量(mm) / 馬達單圈移動量(mm) x 360(deg) / 步數(step)
            # EX. conversion = 1000 / (12 * pi) * (360 / 200)
            #Hconversion = 1000 * (12 * pi) * 360
            #Vconversion = 1000 * (47 * pi) * 360
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
            self.listWidget_results_window.addItem(f"[INFO] X: {x:.04f}, Y: {y:.04f}, Z: {z:.04f}")
        thread = Thread(target=do, args=(self.value_x.value(), self.value_y.value(), self.value_z.value()))
        thread.start()

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
