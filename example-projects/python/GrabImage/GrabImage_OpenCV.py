import sys
import threading
import msvcrt
import numpy as np
import cv2
import time
from ctypes import *

sys.path.append("MvImport")
from MvCameraControl_class import *

g_bExit = False  # Global flag to exit the image capture loop
scale = 0

def get_frame(cam):
    """Function to acquire a frame from the camera."""
    stOutFrame = MV_FRAME_OUT()  # Create a structure to hold the image frame
    memset(byref(stOutFrame), 0, sizeof(stOutFrame))  # Initialize the structure

    # Capture an image from the camera
    ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)

    if ret != 0:
        print(f"Frame not acquired! ret[0x{ret:x}]")
        return None

    start_time = time.time()
    # Cache the image buffer in a byte array
    buf_cache = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
    memmove(byref(buf_cache), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)

    # Convert the buffer into a NumPy array and reshape it to image dimensions
    np_image = np.ctypeslib.as_array(buf_cache)
    np_image = np_image.reshape((stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nWidth))

    # Convert the image from BayerRG to RGB
    rgb_image = cv2.cvtColor(np_image, cv2.COLOR_BayerRG2RGB)

    print(f"Color conversion duration = {time.time() - start_time:.5f}")

    # Free the image buffer after use
    cam.MV_CC_FreeImageBuffer(stOutFrame)

    return rgb_image  # Return the processed image

def work_thread(cam=0, pData=0, nDataSize=0):
    """Thread function to capture and display images continuously."""
    global scale
    global g_bExit
    
    cv2.namedWindow("Captured Image")
    cv2.createTrackbar("Exposure Time", "Captured Image", int(8000), int(exposure_max), on_trackbar_exposure)
    cv2.createTrackbar("Gain", "Captured Image", int(0), int(gain_max), on_trackbar_gain)

    while not g_bExit:
        # Capture a frame from the camera
        frame = get_frame(cam)
        if frame is not None:
            # Resize the frame based on the scale
            width = int(frame.shape[1] * scale / 100)
            height = int(frame.shape[0] * scale / 100)
            img = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

            # Display the captured frame
            cv2.imshow("Captured Image", img)
            if cv2.waitKey(1) == 27:
                g_bExit = True  # Set the global flag to exit the loop
                break


def set_camera_settings(cam):
    """Function to set the default camera settings."""
    # Set Gain and Exposure to manual mode
    cam.MV_CC_SetEnumValue("GainAuto", 0)
    cam.MV_CC_SetEnumValue("ExposureAuto", 0)

    # Set specific values for Gain and Exposure time
    cam.MV_CC_SetFloatValue("Gain", 0.0)
    cam.MV_CC_SetFloatValue("ExposureTime", 8000.0)  # Set exposure to 8000 microseconds


def get_exposure_limits(cam):
    """Function to get the exposure time limits from the camera."""
    stParam = MVCC_FLOATVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_FLOATVALUE))
    ret = cam.MV_CC_GetFloatValue("ExposureTime", stParam)
    if ret != 0:
        print(f"Get Exposure Time fail! ret[0x{ret:x}]")
        return None
    return stParam.fMin, stParam.fMax

def get_gain_limits(cam):
    """Function to get the gain limits from the camera."""
    stParam = MVCC_FLOATVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_FLOATVALUE))
    ret = cam.MV_CC_GetFloatValue("Gain", stParam)
    if ret != 0:
        print(f"Get Gain fail! ret[0x{ret:x}]")
        return None
    return stParam.fMin, stParam.fMax

def on_trackbar_exposure(val):
    """Callback function for exposure trackbar."""
    try:
        cam.MV_CC_SetFloatValue("ExposureTime", float(val))
        print(f"Exposure Time set to: {val}")
    except Exception as e:
        print(f"Error setting Exposure Time: {e}")

def on_trackbar_gain(val):
    """Callback function for gain trackbar."""
    try:
        cam.MV_CC_SetFloatValue("Gain", float(val))
        print(f"Gain set to: {val}")
    except Exception as e:
        print(f"Error setting Gain: {e}")


if __name__ == "__main__":
    """Main function to initialize the camera and start capturing images."""
    # Initialize the camera SDK
    MvCamera.MV_CC_Initialize()

    deviceList = MV_CC_DEVICE_INFO_LIST()  # Create a device info list
    tlayerType = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                  | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)

    scale = int(input("Enter a scale for window and press enter: "))  # Scale factor for image resizing

    # Enumerate all connected devices
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print("enum devices fail! ret[0x%x]" % ret)
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print("find no device!")
        sys.exit()

    print("Find %d devices!" % deviceList.nDeviceNum)

    # Print information about each device
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
            print("\ngige device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("user serial number: %s" % strSerialNumber)
        # Similar checks for other device types...

    # Get the user's choice for which device to connect
    nConnectionNum = input("please input the number of the device to connect: ")

    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print("input error!")
        sys.exit()

    # Create Camera Object
    cam = MvCamera()

    # Select the device and create a handle for it
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print("create handle fail! ret[0x%x]" % ret)
        sys.exit()

    # Open the selected camera device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("open device fail! ret[0x%x]" % ret)
        sys.exit()

    set_camera_settings(cam)  # Apply camera settings

    # Set optimal packet size for GigE cameras
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE or stDeviceList.nTLayerType == MV_GENTL_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
            if ret != 0:
                print("Warning: Set Packet Size fail! ret[0x%x]" % ret)
        else:
            print("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

    # Get frame rate settings for the camera
    stBool = c_bool(False)
    ret = cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
    if ret != 0:
        print("get AcquisitionFrameRateEnable fail! ret[0x%x]" % ret)

    # Set trigger mode to off
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()


    exposure_min, exposure_max = get_exposure_limits(cam)
    print(f"Exposure time limits: {exposure_min} to {exposure_max} microseconds")

    gain_min, gain_max = get_gain_limits(cam)
    print(f"Gain limits: {gain_min} to {gain_max}")

    # Start grabbing images
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print("start grabbing fail! ret[0x%x]" % ret)
        sys.exit()

    

    try:
        # Start a new thread to handle image capture
        hThreadHandle = threading.Thread(target=work_thread, args=(cam, None, None))
        hThreadHandle.start()
    except:
        print("error: unable to start thread")

    # Wait for a key press to stop the image capture
    print("press the Escape key to stop grabbing.")
    while not g_bExit:
        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 27:  # Escape key
                g_bExit = True

    hThreadHandle.join()  # Wait for the thread to finish

    # Stop grabbing images
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print("stop grabbing fail! ret[0x%x]" % ret)
        sys.exit()

    # Close the camera device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print("close device fail! ret[0x%x]" % ret)
        sys.exit()

    # Destroy the camera handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print("destroy handle fail! ret[0x%x]" % ret)
        sys.exit()

    # Finalize the camera SDK
    MvCamera.MV_CC_Finalize()
