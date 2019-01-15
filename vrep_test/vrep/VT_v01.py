# -*- coding: utf-8 -*-

from typing import Tuple
from math import sqrt, pi
from threading import Thread
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from . import vrep
from .Ui_VT_v01 import Ui_Dialog

CLIENT_ID = -1


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
    return vrep.simxGetObjectPosition(CLIENT_ID, handle, -1, vrep.simx_opmode_oneshot_wait)


@_no_error
def set_pos(x: float, y: float, z: float, handle: object) -> None:
    return vrep.simxSetObjectPosition(CLIENT_ID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)


class ControlPanel(QDialog, Ui_Dialog):

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.setupUi(self)
        self.main()

    @pyqtSlot(name='on_print_clicked')
    def print_go(self):
        print('OK!!!')
        self.listWidget_results_window.addItem("123test123")

    @pyqtSlot(name='on_with_start_clicked')
    def with_go(self):
        def do(dx, dy, dz):
            d = sqrt(dx * dx + dy * dy + dz * dz)
            handle, handle_value = vrep.simxGetObjectHandle(CLIENT_ID, "box", vrep.simx_opmode_oneshot_wait)
            if d == 0:
                return

            # 移動量
            tx = dx / d
            ty = dy / d
            tz = dz / d

            # EX. 馬達脈波:  移動量(mm) / 馬達單圈移動量(mm) x 360(deg) / 步數(step)
            # EX. conversion = 1000 / (12 * pi) * (360 / 200)
            conversion = 1000 / (12 * 12 * pi) * 360
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

            for _ in range(int(ds)):
                x, y, z = get_pos(handle_value)
                set_pos(x + tx * step, y + ty * step, z + tz * step, handle_value)

            x, y, z = get_pos(handle_value)
            print(f'StepMotor_X: {cx:.04f} deg')
            print(f'StepMotor_Y: {cy:.04f} deg')
            print(f'StepMotor_Z: {cz:.04f} deg')
            set_pos(x + fx, y + fy, z + fz, handle_value)
            self.listWidget_results_window.addItem(f"(X: {x + fx:.04f}, Y: {y + fy:.04f}, Z: {z + fz:.04f})")

        thread = Thread(target=do, args=(self.value_x.value(), self.value_y.value(), self.value_z.value()))
        thread.start()

    def main(self):
        vrep.simxFinish(-1)
        global CLIENT_ID
        CLIENT_ID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if CLIENT_ID == -1:
            print('Failed connecting to remote API server')
            return
        print('Connected to remote API server')
        res, objs = vrep.simxGetObjects(CLIENT_ID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
        if res == vrep.simx_return_ok:
            print(f'Number of objects in the scene: {len(objs)}')
        else:
            print(f'Remote API function call returned with error code: {res}')
        # Initialize streaming
        vrep.simxGetIntegerParameter(CLIENT_ID, vrep.sim_intparam_mouse_x, vrep.simx_opmode_streaming)
        vrep.simxAddStatusbarMessage(CLIENT_ID, 'Hello V-REP!', vrep.simx_opmode_oneshot)
        vrep.simxGetPingTime(CLIENT_ID)
