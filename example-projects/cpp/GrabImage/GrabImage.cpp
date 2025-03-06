#include <iostream>
#include <opencv2/opencv.hpp>
#include "MvCameraControl.h"
#include <thread>
#include <atomic>

std::atomic<bool> g_bExit(false);

cv::Mat GetFrame(void* handle) {
    MV_FRAME_OUT stOutFrame;
    memset(&stOutFrame, 0, sizeof(stOutFrame));
    
    int ret = MV_CC_GetImageBuffer(handle, &stOutFrame, 1000);
    if (ret != MV_OK) {
        std::cerr << "Frame not acquired! ret[0x" << std::hex << ret << "]\n";
        return cv::Mat();
    }
    
    cv::Mat img(stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nWidth, CV_8UC1, stOutFrame.pBufAddr);
    cv::Mat bgrImage;
    cv::cvtColor(img, bgrImage, cv::COLOR_BayerRG2RGB);
    
    MV_CC_FreeImageBuffer(handle, &stOutFrame);
    return bgrImage;
}

void WorkThread(void* handle) {
    int scale = 50;
    while (!g_bExit) {
        cv::Mat frame = GetFrame(handle);
        if (!frame.empty()) {
            cv::resize(frame, frame, cv::Size(frame.cols * scale / 100, frame.rows * scale / 100));
            cv::imshow("Captured Image", frame);
            cv::waitKey(1);
        }
    }
}

void SetCameraSettings(void* handle) {
    MV_CC_SetEnumValue(handle, "GainAuto", 0);
    MV_CC_SetEnumValue(handle, "ExposureAuto", 0);
    MV_CC_SetFloatValue(handle, "Gain", 0.0);
    MV_CC_SetFloatValue(handle, "ExposureTime", 100000);
}

int main() {
    MV_CC_Initialize();
    MV_CC_DEVICE_INFO_LIST deviceList;
    int ret = MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, &deviceList);
    if (ret != MV_OK || deviceList.nDeviceNum == 0) {
        std::cerr << "No devices found!\n";
        return -1;
    }
    
    void* cam;
    MV_CC_CreateHandle(&cam, deviceList.pDeviceInfo[0]);
    MV_CC_OpenDevice(cam, MV_ACCESS_Exclusive, 0);
    SetCameraSettings(cam);
    
    MV_CC_StartGrabbing(cam);
    std::thread worker(WorkThread, cam);
    
    std::cout << "Press Enter to stop...";
    std::cin.get();
    g_bExit = true;
    worker.join();
    
    MV_CC_StopGrabbing(cam);
    MV_CC_CloseDevice(cam);
    MV_CC_DestroyHandle(cam);
    MV_CC_Finalize();
    return 0;
}
