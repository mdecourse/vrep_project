import vrep
from time import sleep
from math import sqrt


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
    tx = dx / d
    ty = dy / d
    tz = dz / d

    step = 0.1
    for i in range(int(d // step * 10)):
        ok, pos = get_pos(clientID, handle)
        if ok == vrep.simx_return_ok:
            x, y, z = pos
            set_pos(x + tx * step / 10, y + ty * step / 10, z + tz * step / 10, clientID, handle)
    
    #f = d % step
    ok, pos = get_pos(clientID, handle)
    if ok == vrep.simx_return_ok:
        x, y, z = pos
    #set_pos(x + f, y + f, z + f, clientID, handle)


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
    vrep.simxFinish(-1) # just in case, close all opened connections
    clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5) # Connect to V-REP

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
    #err, Cub1_handle = vrep.simxGetObjectHandle(clientID, "Cub1", vrep.simx_opmode_oneshot_wait)
    #err, nozzle_handle = vrep.simxGetObjectHandle(clientID, "nozzle", vrep.simx_opmode_oneshot_wait)
    err, plate_handle = vrep.simxGetObjectHandle(clientID, "plate", vrep.simx_opmode_oneshot_wait)
    
    # M path
    # m_path(30, clientID, Cub1_handle)
    #walk_to(0, 0, 0.5, clientID, Cub1_handle)
    # walk_with(1, 0, 0, clientID, Cub1_handle)
    walk_with(0.2, 0.3, 0, clientID, plate_handle)
    walk_with(0.2, -0.3, 0, clientID, plate_handle)
    walk_with(-0.4, 0, 0, clientID, plate_handle)
    walk_with(0, -0.05, 0, clientID, plate_handle)
    walk_with(0, -0.05, 0, clientID, plate_handle)


    # Now send some data to V-REP in a non-blocking fashion:
    vrep.simxAddStatusbarMessage(clientID, 'Hello V-REP!', vrep.simx_opmode_oneshot)

    # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    vrep.simxGetPingTime(clientID)

    # Now close the connection to V-REP:
    vrep.simxFinish(clientID)


if __name__ == '__main__':
    main()
