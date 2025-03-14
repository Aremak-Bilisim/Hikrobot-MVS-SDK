import sys
import ctypes
import numpy as np
import cv2
import time

sys.path.append("../../../common/dependencies/MvImport")
from MvCameraControl_class import *

count = 0
sum = 0


def set_camera_settings(cam):
    # Set camera parameters
    cam.MV_CC_SetBoolValue("HDREnable", True)
    
    
    exposure_values = [5000, 10000, 15000, 20000]
    for i in range(4):
        cam.MV_CC_SetIntValueEx("HDRSelector", i)
        cam.MV_CC_SetIntValueEx("HDRShutter", exposure_values[i])
        cam.MV_CC_SetFloatValue("HDRGain", 0)
    

def getOpenCVImage(cam):
    global count, sum
    # Initialize frame buffer
    stOutFrame = MV_FRAME_OUT()
    ctypes.memset(ctypes.byref(stOutFrame), 0, ctypes.sizeof(stOutFrame))

    ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
    if ret != 0:
        print(f"Failed to get image buffer! Error code: 0x{ret:X}")
        sys.exit()

    start_time = time.time()
    # Convert to OpenCV Image
    buf_cache = (ctypes.c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
    ctypes.memmove(ctypes.byref(buf_cache), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)

    width, height = stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight
    scale_factor = min(1920 / width, 1080 / height)

    np_image = np.ctypeslib.as_array(buf_cache).reshape(height, width)
    cv_image = cv2.cvtColor(np_image, cv2.COLOR_BayerRG2RGB)
    
    
    if (count < 1000):
        sum += (time.time()-start_time)
        count += 1
    elif (count == 1000):
        print(f"Average color conversion time: {(sum / 1000):.7f} seconds")
        count += 1
        
    
    cv_image = cv2.resize(cv_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    cam.MV_CC_FreeImageBuffer(stOutFrame)  # Free buffer after use

    return cv_image



if __name__ == "__main__":
    # Initialize the camera SDK
    MvCamera.MV_CC_Initialize()

    deviceList = MV_CC_DEVICE_INFO_LIST()  # Create a device info list
    tlayerType = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                  | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)


    # Enumerate all connected devices
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print(f"Device enumeration failed! Error code: 0x{ret:X}")
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print("No camera devices found.")
        sys.exit()

    print(f"Found {deviceList.nDeviceNum} device(s).")

    # Print information about each device
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = ctypes.cast(deviceList.pDeviceInfo[i], ctypes.POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
            print(f"\nGigE device: [{i}]")
            strModeName = "".join(chr(per) for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName if per != 0)
            print(f"Device model name: {strModeName}")

            nip1 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24
            nip2 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16
            nip3 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8
            nip4 = mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff
            print(f"Current IP: {nip1}.{nip2}.{nip3}.{nip4}\n")
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print(f"\nUSB device: [{i}]")
            strModeName = "".join(chr(per) for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName if per != 0)
            print(f"Device model name: {strModeName}")

            strSerialNumber = "".join(chr(per) for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber if per != 0)
            print(f"User serial number: {strSerialNumber}")
        # Similar checks for other device types...

    # Get the user's choice for which device to connect
    if deviceList.nDeviceNum == 1:
        nConnectionNum = 0
    
    else: 
        nConnectionNum = int(input("Please input the number of the device to connect: "))

        if nConnectionNum >= deviceList.nDeviceNum:
            print("Input error!")
            sys.exit()

    # Create Camera Object
    cam = MvCamera()

    # Select the device and create a handle for it
    stDeviceList = ctypes.cast(deviceList.pDeviceInfo[nConnectionNum], ctypes.POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print(f"Failed to create handle! Error code: 0x{ret:X}")
        sys.exit()

    # Open the selected camera device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print(f"Failed to open device! Error code: 0x{ret:X}")
        cam.MV_CC_DestroyHandle()
        sys.exit()

    set_camera_settings(cam)  # Apply camera settings

    # Set optimal packet size for GigE cameras
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE or stDeviceList.nTLayerType == MV_GENTL_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
            if ret != 0:
                print(f"Warning: Set Packet Size fail! Error code: 0x{ret:X}")
        else:
            print(f"Warning: Get Packet Size fail! Error code: 0x{nPacketSize:X}")



    # Start Grabbing
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print(f"Failed to start grabbing! Error code: 0x{ret:X}")
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()
        sys.exit()

    print("Camera is grabbing frames... Press ESC to exit.")



    while True:
        frame = getOpenCVImage(cam)
        cv2.imshow("Image", frame)

        exposure = 10000
        gain = 0
        

        cam.MV_CC_SetFloatValue("ExposureTime", float(exposure))
        cam.MV_CC_SetFloatValue("Gain", float(gain))

        if cv2.waitKey(1) == 27:  # Exit on ESC key
            break

    # Cleanup
    cam.MV_CC_StopGrabbing()
    cam.MV_CC_SetBoolValue("HDREnable", False)
    cam.MV_CC_CloseDevice()
    cam.MV_CC_DestroyHandle()
    cv2.destroyAllWindows()
