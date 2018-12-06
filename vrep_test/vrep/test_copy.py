import vrep
from math import sqrt, pi
from time import sleep


def hypot_3d(x, y, z):
    return sqrt(x * x + y * y + z * z)


def get_pos(clientID, handle):
    return vrep.simxGetObjectPosition(clientID, handle, -1, vrep.simx_opmode_oneshot_wait)


def set_pos(x, y, z, clientID, handle):
    vrep.simxSetObjectPosition(clientID, handle, -1, (x, y, z), vrep.simx_opmode_oneshot_wait)


def walk_to(wx, wy, wz, clientID, handle):
    ok, (ox, oy, oz) = get_pos(clientID, handle)
    walk_with(wx - ox, wy - oy, wz - oz, clientID, handle)


def walk_with(dx, dy, dz, clientID, handle):
    d = hypot_3d(dx, dy, dz)
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
    for i in range(int(ds)):
        ok, pos = get_pos(clientID, handle)
        if ok == vrep.simx_return_ok:
            x, y, z = pos
            set_pos(x + tx * step, y + ty * step, z + tz * step, clientID, handle)
    
    # 補正誤差值        
    fx = dx % step
    fy = dy % step
    fz = dz % step        
    ok, pos = get_pos(clientID, handle)
    if ok == vrep.simx_return_ok:
        x, y, z = pos
        print('StepMotor_X :', round(cx, 4), 'deg')
        print('StepMotor_Y :', round(cy, 4), 'deg')
        print('StepMotor_Z :', round(cz, 4), 'deg')
        set_pos(x + fx, y + fy, z + fz, clientID, handle)
        #self.translateShow.addItem("(X: {:.04f},Y: {:.04f},Z: {:.04f})".format(a2z, b2z, c2z))
        
        
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


if __name__ == '__main__':
    main()
