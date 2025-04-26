import sys
import os
import ctypes
import numpy as np
import cv2
import time


# Get the absolute path to the MvImport directory
current_dir = os.path.dirname(os.path.abspath(__file__))
mvimport_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'common', 'dependencies', 'MvImport'))
sys.path.append(mvimport_path)

from MvCameraControl_class import *

count = 0
sum = 0


"""
This script interfaces with a camera using the MvImport library, providing functionalities to set camera settings, convert pixel formats, and retrieve images. The main features include:

### Key Functionalities:
1. **Camera Initialization and Setup**:
   - Initializes the camera SDK.
   - Enumerates and lists all connected camera devices.
   - Allows the user to select a device and connect to it.

2. **Camera Settings Configuration**:
   - Sets initial camera parameters such as exposure time and gain.
   - Provides functions to retrieve exposure and gain limits from the camera.

3. **Pixel Format Conversion**:
   - Converts raw image data to RGB format based on the pixel format.
   - Supports various pixel formats including MONO8, MONO10, MONO12, BAYER formats, RGB/BGR packed formats, and YUV formats.
   - Uses global variables for pixel format constants to ensure consistency in conversions.

4. **Image Retrieval and Display**:
   - Continuously grabs frames from the camera.
   - Displays the frames using OpenCV.
   - Includes error handling for image retrieval and processing.

5. **User Interface for Settings Adjustment**:
   - Creates a trackbar window for adjusting exposure and gain settings in real-time.
   - Updates camera settings based on trackbar inputs.

6. **Resource Management**:
   - Ensures proper cleanup of resources, including stopping image grabbing, closing the device, and destroying the handle.

### Dependencies:
- **MvImport library**: For camera control.
- **OpenCV**: For image processing and display.
- **NumPy**: For numerical operations.
- **ctypes**: For low-level operations.

This script is designed to be robust and includes error handling for various operations to ensure smooth functionality.
"""

def set_camera_settings(cam):
    # Set camera parameters    
    cam.MV_CC_SetEnumValue("TriggerMode", 0)
    cam.MV_CC_SetFloatValue("ExposureTime", 10000.0)  
    cam.MV_CC_SetEnumValue("GainAuto", 0)  


def convert_pixel_format(numpy_array, pixel_format, width, height):
    """
    Convert raw image data to RGB format based on pixel format
    """
    # 8-bit formats
    if pixel_format == PixelType_Gvsp_Mono8:
        img = numpy_array.reshape((height, width))
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    # 10-bit format
    elif pixel_format == PixelType_Gvsp_Mono10:
        # Reshape to 2D array of 16-bit values
        img = numpy_array.view(np.uint16).reshape(height, width)
        # Scale down from 10-bit to 8-bit
        img = (img >> 2).astype(np.uint8)
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    # 12-bit format
    elif pixel_format == PixelType_Gvsp_Mono12:
        # Reshape to 2D array of 16-bit values
        img = numpy_array.view(np.uint16).reshape(height, width)
        # Scale down from 12-bit to 8-bit
        img = (img >> 4).astype(np.uint8)
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    # 8-bit Bayer formats
    elif pixel_format in [PixelType_Gvsp_BayerGR8, PixelType_Gvsp_BayerRG8, 
                         PixelType_Gvsp_BayerGB8, PixelType_Gvsp_BayerBG8]:
        img = numpy_array.reshape((height, width))
        conversion_map = {
            PixelType_Gvsp_BayerGR8: cv2.COLOR_BayerGR2RGB,
            PixelType_Gvsp_BayerRG8: cv2.COLOR_BayerRG2RGB,
            PixelType_Gvsp_BayerGB8: cv2.COLOR_BayerGB2RGB,
            PixelType_Gvsp_BayerBG8: cv2.COLOR_BayerBG2RGB
        }
        return cv2.cvtColor(img, conversion_map[pixel_format])
    
    # 10-bit Bayer formats
    elif pixel_format == PixelType_Gvsp_BayerRG10:
        img = numpy_array.view(np.uint16).reshape(height, width)
        img = (img >> 2).astype(np.uint8)  # Convert 10-bit to 8-bit
        return cv2.cvtColor(img, cv2.COLOR_BayerRG2RGB)
    
    # 10-bit Bayer Packed formats
    elif pixel_format == PixelType_Gvsp_BayerRG10_Packed:
        return numpy_array
    
    # 12-bit Bayer formats
    elif pixel_format == PixelType_Gvsp_BayerRG12:
        img = numpy_array.view(np.uint16).reshape(height, width)
        img = (img >> 4).astype(np.uint8)  # Convert 12-bit to 8-bit
        return cv2.cvtColor(img, cv2.COLOR_BayerRG2RGB)
    
    # 12-bit Bayer Packed formats
    # elif pixel_format == PixelType_Gvsp_BayerRG12_Packed:
    #     print("Bayer12")
    #     img = numpy_array.view(np.uint16).reshape(height, width)
    #     img = (img >> 4).astype(np.uint8)  # Convert 12-bit to 8-bit
    #     return cv2.cvtColor(img, cv2.COLOR_BayerRG2RGB)
    
    # Packed RGB/BGR formats
    elif pixel_format == PixelType_Gvsp_RGB8_Packed:
        return cv2.cvtColor(numpy_array.reshape((height, width, 3)), cv2.COLOR_RGB2BGR)
    
    elif pixel_format == PixelType_Gvsp_BGR8_Packed:
        img = numpy_array.reshape((height, width, 3))
        return img
    
    # YUV formats YUY422 Packed
    elif pixel_format == PixelType_Gvsp_YUV422_Packed:
        # First convert to uint8 and reshape to proper dimensions
        data = numpy_array.astype(np.uint8)
        # YUYV format has 2 bytes per pixel, so width needs to be doubled
        data = data.reshape((height, width, 2))
        # Convert from YUV to BGR
        bgr_img = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_UYVY)
        return bgr_img
    
    # YUV formats YUY422 
    elif pixel_format == PixelType_Gvsp_YUV422_YUYV_Packed:
        # First convert to uint8 and reshape to proper dimensions
        data = numpy_array.astype(np.uint8)
        # YUYV format has 2 bytes per pixel, so width needs to be doubled
        data = data.reshape((height, width, 2))
        # Convert from YUV to BGR
        bgr_img = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_YUYV)
        return bgr_img

    
    else:
        raise ValueError(f"Unsupported pixel format: {pixel_format}")
    


def getOpenCVImage(cam):
    global count, sum
    stOutFrame = MV_FRAME_OUT()
    ctypes.memset(ctypes.byref(stOutFrame), 0, ctypes.sizeof(stOutFrame))

    ret = cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
    if ret != 0:
        print(f"Failed to get image buffer! Error code: 0x{ret:X}")
        return None

    start_time = time.time()
    try:
        buf_cache = (ctypes.c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
        ctypes.memmove(ctypes.byref(buf_cache), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nFrameLen)
        
        width = stOutFrame.stFrameInfo.nWidth
        height = stOutFrame.stFrameInfo.nHeight
        pixel_format = stOutFrame.stFrameInfo.enPixelType

        numpy_array = np.ctypeslib.as_array(buf_cache)
        
        # Pixel format conversions
        cv_image = convert_pixel_format(numpy_array, pixel_format, width, height)

        if count < 1000:
            sum += (time.time()-start_time)
            count += 1
        elif count == 1000:
            print(f"Average color conversion time: {(sum / 1000):.7f} seconds")
            count += 1

        scale_factor = min(1920 / width, 1080 / height)
        cv_image = cv2.resize(cv_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    except Exception as e:
        print(f"Error processing image: {e}")
        cv_image = None
    finally:
        cam.MV_CC_FreeImageBuffer(stOutFrame)

    return cv_image

def create_trackbar(min_e, max_e, min_g, max_g):
    
    
    maxAllowedExposure = 1000000
    
    cv2.namedWindow("Settings", cv2.WINDOW_NORMAL)
    
    # Since higher values of exposure makes the program laggy, we have limited it to maxAllowedExposure.
    if (max_e >= maxAllowedExposure): 
        cv2.createTrackbar("Exposure", "Settings", int(min_e), int(maxAllowedExposure), lambda x: None)
    else:
        cv2.createTrackbar("Exposure", "Settings", int(min_e), int(max_e), lambda x: None)
 
    cv2.createTrackbar("Gain", "Settings", int(min_g), int(max_g), lambda x: None)
    
    cam.MV_CC_SetFloatValue("ExposureTime", float(min_e))
    cam.MV_CC_SetFloatValue("Gain", float(min_g))
    cv2.setTrackbarPos("Exposure", "Settings", int(min_e))
    cv2.setTrackbarPos("Gain", "Settings", int(min_g))

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
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
            print ("\ngige device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))

        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print ("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)
            
        elif mvcc_dev_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
            print ("\nCML device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stCMLInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stCMLInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)
            
        elif mvcc_dev_info.nTLayerType == MV_GENTL_CXP_DEVICE:
            print ("\nCXP device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stCXPInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stCXPInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)
            
        elif mvcc_dev_info.nTLayerType == MV_GENTL_XOF_DEVICE:
            print ("\nXoF device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stXoFInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stXoFInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)

    # Get the user's choice for which device to connect
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

    # Set optimal packet size for GigE cameras
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE or stDeviceList.nTLayerType == MV_GENTL_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
            if ret != 0:
                print(f"Warning: Set Packet Size fail! Error code: 0x{ret:X}")
        else:
            print(f"Warning: Get Packet Size fail! Error code: 0x{nPacketSize:X}")


    set_camera_settings(cam)  # Apply camera settings
    
    exposure_min, exposure_max = get_exposure_limits(cam)
    gain_min, gain_max = get_gain_limits(cam)


    # Start Grabbing
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print(f"Failed to start grabbing! Error code: 0x{ret:X}")
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()
        sys.exit()

    print("Camera is grabbing frames... Press ESC to exit.")

    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    create_trackbar(exposure_min, exposure_max, gain_min, gain_max)


    while True:
        frame = getOpenCVImage(cam)
        cv2.imshow("Image", frame)

        exposure = cv2.getTrackbarPos("Exposure", "Settings")
        gain = cv2.getTrackbarPos("Gain", "Settings")

        cam.MV_CC_SetFloatValue("ExposureTime", float(exposure))
        cam.MV_CC_SetFloatValue("Gain", float(gain))

        if cv2.waitKey(1) == 27:  # Exit on ESC key
            break

    # Cleanup
    cam.MV_CC_StopGrabbing()
    cam.MV_CC_CloseDevice()
    cam.MV_CC_DestroyHandle()
    cv2.destroyAllWindows()
