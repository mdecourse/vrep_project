try:
    import vrep
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time
#import matplotlib.pyplot as plt

x = []
y = []
z = []

print ('Program started')
vrep.simxFinish(-1) # just in case, close all opened connections
clientID=vrep.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP
if clientID!=-1:
    print ('Connected to remote API server')
    # Now try to retrieve data in a blocking fashion (i.e. a service call):
    res,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_blocking)
    if res==vrep.simx_return_ok:
        print ('Number of objects in the scene: ',len(objs))
    else:
        print ('Remote API function call returned with error code: ',res)

    time.sleep(2)

    # Now retrieve streaming data (i.e. in a non-blocking fashion):
    startTime=time.time()
    vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) # Initialize streaming
    err, Cub1_handle = vrep.simxGetObjectHandle(clientID, "Cub1", vrep.simx_opmode_oneshot_wait)
    
    number = 40
    step = 0
    for i in range(number):
        step += 1
        #returnCode,data=vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_buffer) # Try to retrieve the streamed data
        returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
        if returncode_pos==vrep.simx_return_ok: # After initialization of streaming, it will take a few ms before the first value arrives, so check the return code
            waitforfinish = vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, (0, 0.015*step, 0.05), vrep.simx_opmode_oneshot_wait)
            print(data_pos)
    step = 0
    for i in range(number):
        step += 1
        returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
        if returncode_pos==vrep.simx_return_ok: 
            waitforfinish = vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, (0.015*step, 0.015*number, 0.05), vrep.simx_opmode_oneshot_wait)
            print(data_pos)
    for i in range(number):
        step -= 1
        returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
        if returncode_pos==vrep.simx_return_ok: 
            waitforfinish = vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, (0.015*number, 0.015*step, 0.05), vrep.simx_opmode_oneshot_wait)
            print(data_pos)
    step = number
    for i in range(number):
        step -= 1
        returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle, -1, vrep.simx_opmode_oneshot_wait)
        if returncode_pos==vrep.simx_return_ok: 
            waitforfinish = vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, (0.015*step, 0, 0.05), vrep.simx_opmode_oneshot_wait)
            print(data_pos)
            
            #x.append(data_pos[0])
            #y.append(data_pos[0])
            
    #while time.time()-startTime < 5:
     #   step += 1
        #returnCode,data=vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_buffer) # Try to retrieve the streamed data
     #   returncode_pos, data_pos = vrep.simxGetObjectPosition(clientID, Cub1_handle , -1, vrep.simx_opmode_oneshot_wait)
      #  if returncode_pos==vrep.simx_return_ok: # After initialization of streaming, it will take a few ms before the first value arrives, so check the return code
       #     waitforfinish = vrep.simxSetObjectPosition(clientID, Cub1_handle, -1, (0.05 * step, 0.05 * step, 0.05), vrep.simx_opmode_oneshot_wait)
        #    print(data_pos)
         #   x.append(data_pos[0])
          #  y.append(data_pos[0])
           # time.sleep(0.005)

    # Now send some data to V-REP in a non-blocking fashion:
    vrep.simxAddStatusbarMessage(clientID,'Hello V-REP!',vrep.simx_opmode_oneshot)

    # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    vrep.simxGetPingTime(clientID)

    # Now close the connection to V-REP:
    vrep.simxFinish(clientID)
    #plt.plot(x, y)
    #plt.show()
else:
    print ('Failed connecting to remote API server')
print ('Program ended')
