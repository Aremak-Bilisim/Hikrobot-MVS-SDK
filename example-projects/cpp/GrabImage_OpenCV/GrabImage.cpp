﻿#include <stdio.h>
#include <process.h>
#include <conio.h>
#include "windows.h"
#include <chrono>
#include "MvCameraControl.h"
#include <opencv2/opencv.hpp>


bool g_bExit = false;
int minExposure = 0;
int minGain = 0;
int maxExposure = 80000;
int maxGain = 50;
int maxAllowedExposure = 1000000;
int count = 0;
double sum = 0.0;



void WaitForKeyPress(void)
{
	while (!_kbhit())
	{
		Sleep(10);
	}
	_getch();
}

bool PrintDeviceInfo(MV_CC_DEVICE_INFO* pstMVDevInfo)
{
	if (NULL == pstMVDevInfo)
	{
		printf("The Pointer of pstMVDevInfo is NULL!\n");
		return false;
	}
	if (pstMVDevInfo->nTLayerType == MV_GIGE_DEVICE)
	{
		int nIp1 = ((pstMVDevInfo->SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24);
		int nIp2 = ((pstMVDevInfo->SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16);
		int nIp3 = ((pstMVDevInfo->SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8);
		int nIp4 = (pstMVDevInfo->SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff);

		printf("CurrentIp: %d.%d.%d.%d\n", nIp1, nIp2, nIp3, nIp4);
		printf("UserDefinedName: %s\n\n", pstMVDevInfo->SpecialInfo.stGigEInfo.chUserDefinedName);
	}
	else if (pstMVDevInfo->nTLayerType == MV_USB_DEVICE)
	{
		printf("UserDefinedName: %s\n", pstMVDevInfo->SpecialInfo.stUsb3VInfo.chUserDefinedName);
		printf("Serial Number: %s\n", pstMVDevInfo->SpecialInfo.stUsb3VInfo.chSerialNumber);
		printf("Device Number: %d\n\n", pstMVDevInfo->SpecialInfo.stUsb3VInfo.nDeviceNumber);
	}
	else if (pstMVDevInfo->nTLayerType == MV_GENTL_GIGE_DEVICE)
	{
		printf("UserDefinedName: %s\n", pstMVDevInfo->SpecialInfo.stGigEInfo.chUserDefinedName);
		printf("Serial Number: %s\n", pstMVDevInfo->SpecialInfo.stGigEInfo.chSerialNumber);
		printf("Model Name: %s\n\n", pstMVDevInfo->SpecialInfo.stGigEInfo.chModelName);
	}
	else if (pstMVDevInfo->nTLayerType == MV_GENTL_CAMERALINK_DEVICE)
	{
		printf("UserDefinedName: %s\n", pstMVDevInfo->SpecialInfo.stCMLInfo.chUserDefinedName);
		printf("Serial Number: %s\n", pstMVDevInfo->SpecialInfo.stCMLInfo.chSerialNumber);
		printf("Model Name: %s\n\n", pstMVDevInfo->SpecialInfo.stCMLInfo.chModelName);
	}
	else if (pstMVDevInfo->nTLayerType == MV_GENTL_CXP_DEVICE)
	{
		printf("UserDefinedName: %s\n", pstMVDevInfo->SpecialInfo.stCXPInfo.chUserDefinedName);
		printf("Serial Number: %s\n", pstMVDevInfo->SpecialInfo.stCXPInfo.chSerialNumber);
		printf("Model Name: %s\n\n", pstMVDevInfo->SpecialInfo.stCXPInfo.chModelName);
	}
	else if (pstMVDevInfo->nTLayerType == MV_GENTL_XOF_DEVICE)
	{
		printf("UserDefinedName: %s\n", pstMVDevInfo->SpecialInfo.stXoFInfo.chUserDefinedName);
		printf("Serial Number: %s\n", pstMVDevInfo->SpecialInfo.stXoFInfo.chSerialNumber);
		printf("Model Name: %s\n\n", pstMVDevInfo->SpecialInfo.stXoFInfo.chModelName);
	}
	else
	{
		printf("Not support.\n");
	}

	return true;
}


cv::Mat convertPixelFormat(unsigned char* buffer, int pixelFormat, int width, int height) {
	cv::Mat image;

	switch (pixelFormat) {
	case PixelType_Gvsp_Mono8: {
		image = cv::Mat(height, width, CV_8UC1, buffer);
		cv::cvtColor(image, image, cv::COLOR_GRAY2BGR);
		break;
	}
	case PixelType_Gvsp_Mono10: {
		cv::Mat img(height, width, CV_16UC1, buffer);
		img.convertTo(img, CV_8U, 1.0 / 4); // Scale down from 10-bit to 8-bit
		cv::cvtColor(img, image, cv::COLOR_GRAY2BGR);
		break;
	}
	case PixelType_Gvsp_Mono12: {
		cv::Mat img(height, width, CV_16UC1, buffer);
		img.convertTo(img, CV_8U, 1.0 / 16); // Scale down from 12-bit to 8-bit
		cv::cvtColor(img, image, cv::COLOR_GRAY2BGR);
		break;
	}
	case PixelType_Gvsp_BayerGR8:
	case PixelType_Gvsp_BayerRG8:
	case PixelType_Gvsp_BayerGB8:
	case PixelType_Gvsp_BayerBG8: {
		image = cv::Mat(height, width, CV_8UC1, buffer);
		int code = 0;
		switch (pixelFormat) {
		case PixelType_Gvsp_BayerGR8: code = cv::COLOR_BayerGR2BGR; break;
		case PixelType_Gvsp_BayerRG8: code = cv::COLOR_BayerRG2RGB; break;
		case PixelType_Gvsp_BayerGB8: code = cv::COLOR_BayerGB2BGR; break;
		case PixelType_Gvsp_BayerBG8: code = cv::COLOR_BayerBG2BGR; break;
		}
		cv::cvtColor(image, image, code);
		break;
	}
	case PixelType_Gvsp_BayerRG10: {
		cv::Mat img(height, width, CV_16UC1, buffer);
		img.convertTo(img, CV_8U, 1.0 / 4); // Convert 10-bit to 8-bit
		cv::cvtColor(img, image, cv::COLOR_BayerRG2RGB);
		break;
	}
	case PixelType_Gvsp_BayerRG10_Packed: {
		// Handle packed 10-bit Bayer format
		// This requires specific unpacking logic, not implemented here
		break;
	}
	case PixelType_Gvsp_BayerRG12: {
		cv::Mat img(height, width, CV_16UC1, buffer);
		img.convertTo(img, CV_8U, 1.0 / 16); // Convert 12-bit to 8-bit
		cv::cvtColor(img, image, cv::COLOR_BayerRG2RGB);
		break;
	}
	case PixelType_Gvsp_RGB8_Packed: {
		image = cv::Mat(height, width, CV_8UC3, buffer);
		cv::cvtColor(image, image, cv::COLOR_RGB2BGR);
		break;
	}
	case PixelType_Gvsp_BGR8_Packed: {
		image = cv::Mat(height, width, CV_8UC3, buffer);
		break;
	}
	case PixelType_Gvsp_YUV422_Packed: {
		cv::Mat data(height, width, CV_8UC2, buffer);
		cv::cvtColor(data, image, cv::COLOR_YUV2BGR_UYVY);
		break;
	}


	case PixelType_Gvsp_YUV422_YUYV_Packed: {
		cv::Mat data(height, width, CV_8UC2, buffer);
		cv::cvtColor(data, image, cv::COLOR_YUV2BGR_YUYV);
		break;
	}
	default:
		throw std::runtime_error("Unsupported pixel format");
	}

	return image;
}

static unsigned int __stdcall WorkThread(void* pUser)
{
	int nRet = MV_OK;
	MV_FRAME_OUT stImageInfo = { 0 };
	cv::Mat image;

	// Create a window for the trackbars
	cv::namedWindow("Camera Controls", cv::WINDOW_NORMAL);
	cv::namedWindow("Display", cv::WINDOW_NORMAL);


	// Create trackbars for exposure and gain
	cv::createTrackbar("Exposure", "Camera Controls", &minExposure,
		static_cast<int>(maxExposure), nullptr);
	cv::createTrackbar("Gain", "Camera Controls", &minGain,
		static_cast<int>(maxGain), nullptr);

	while (1)
	{
		nRet = MV_CC_GetImageBuffer(pUser, &stImageInfo, 1000);

		if (nRet == MV_OK)
		{
			auto startTime = std::chrono::high_resolution_clock::now();

			cv::Mat image = convertPixelFormat(stImageInfo.pBufAddr, stImageInfo.stFrameInfo.enPixelType, stImageInfo.stFrameInfo.nWidth, stImageInfo.stFrameInfo.nHeight);

			// Calculate the scaling factor to fit the image within the window
			int width = stImageInfo.stFrameInfo.nWidth;
			int height = stImageInfo.stFrameInfo.nHeight;
			double scale_factor_width = 1920.0 / width;
			double scale_factor_height = 1080.0 / height;
			double scale_factor = std::min(scale_factor_width, scale_factor_height);

			// Resize the image using the scale factor
			cv::Mat resizedImage;
			cv::resize(image, resizedImage, cv::Size(), scale_factor, scale_factor, cv::INTER_LINEAR);

			auto endTime = std::chrono::high_resolution_clock::now();

			std::chrono::duration<double> elapsed = endTime - startTime;
			count++;

			if (count < 1000)
				sum += elapsed.count();
			else if (count == 1000)
				std::cout << "Average color conversion time: " << sum / 1000 << " seconds" << std::endl;

			// Display the image using OpenCV
			cv::imshow("Display", resizedImage);
			cv::waitKey(1);

			nRet = MV_CC_FreeImageBuffer(pUser, &stImageInfo);
			if (nRet != MV_OK)
			{
				printf("Free Image Buffer fail! nRet [0x%x]\n", nRet);
			}
		}
		else
		{
			printf("Get Image fail! nRet [0x%x]\n", nRet);
		}
		if (g_bExit)
		{
			break;
		}

		// Check if trackbar values have changed
		int currentExposure = cv::getTrackbarPos("Exposure", "Camera Controls");
		int currentGain = cv::getTrackbarPos("Gain", "Camera Controls");

		nRet = MV_CC_SetFloatValue(pUser, "ExposureTime", static_cast<float>(currentExposure));
		nRet = MV_CC_SetFloatValue(pUser, "Gain", static_cast<float>(currentGain));
	}

	return 0;
}

void GetExposureLimits(void* handle, int& minExposure, int& maxExposure)
{
	MVCC_FLOATVALUE stParam = { 0 };
	int nRet = MV_CC_GetFloatValue(handle, "ExposureTime", &stParam);
	if (MV_OK != nRet)
	{
		printf("Get Exposure Time fail! nRet [0x%x]\n", nRet);
		minExposure = 0;
		maxExposure = 0;
	}
	else
	{
		minExposure = static_cast<int>(stParam.fMin);
		maxExposure = static_cast<int>(stParam.fMax);
	}
}

void GetGainLimits(void* handle, int& minGain, int& maxGain)
{
	MVCC_FLOATVALUE stParam = { 0 };
	int nRet = MV_CC_GetFloatValue(handle, "Gain", &stParam);
	if (MV_OK != nRet)
	{
		printf("Get Gain fail! nRet [0x%x]\n", nRet);
		minGain = 0;
		maxGain = 0;
	}
	else
	{
		minGain = static_cast<int>(stParam.fMin);
		maxGain = static_cast<int>(stParam.fMax);
	}
}

int main()
{
	int nRet = MV_OK;
	void* handle = NULL;
	do
	{
		nRet = MV_CC_Initialize();
		if (MV_OK != nRet)
		{
			printf("Initialize SDK fail! nRet [0x%x]\n", nRet);
			break;
		}

		MV_CC_DEVICE_INFO_LIST stDeviceList = { 0 };
		nRet = MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE, &stDeviceList);
		if (MV_OK != nRet)
		{
			printf("Enum Devices fail! nRet [0x%x]\n", nRet);
			break;
		}

		if (stDeviceList.nDeviceNum > 0)
		{
			for (unsigned int i = 0; i < stDeviceList.nDeviceNum; i++)
			{
				printf("[device %d]:\n", i);
				MV_CC_DEVICE_INFO* pDeviceInfo = stDeviceList.pDeviceInfo[i];
				if (NULL == pDeviceInfo)
				{
					break;
				}
				PrintDeviceInfo(pDeviceInfo);
			}
		}
		else
		{
			printf("Find No Devices!\n");
			break;
		}

		printf("Please Input camera index(0-%d): ", stDeviceList.nDeviceNum - 1);
		unsigned int nIndex = 0;
		scanf_s("%d", &nIndex);

		if (nIndex >= stDeviceList.nDeviceNum)
		{
			printf("Input error!\n");
			break;
		}

		nRet = MV_CC_CreateHandle(&handle, stDeviceList.pDeviceInfo[nIndex]);
		if (MV_OK != nRet)
		{
			printf("Create Handle fail! nRet [0x%x]\n", nRet);
			break;
		}

		nRet = MV_CC_OpenDevice(handle);
		if (MV_OK != nRet)
		{
			printf("Open Device fail! nRet [0x%x]\n", nRet);
			break;
		}

		if (stDeviceList.pDeviceInfo[nIndex]->nTLayerType == MV_GIGE_DEVICE)
		{
			int nPacketSize = MV_CC_GetOptimalPacketSize(handle);
			if (nPacketSize > 0)
			{
				nRet = MV_CC_SetIntValueEx(handle, "GevSCPSPacketSize", nPacketSize);
				if (nRet != MV_OK)
				{
					printf("Warning: Set Packet Size fail nRet [0x%x]!", nRet);
				}
			}
			else
			{
				printf("Warning: Get Packet Size fail nRet [0x%x]!", nPacketSize);
			}
		}

		nRet = MV_CC_SetEnumValue(handle, "TriggerMode", 0);
		if (MV_OK != nRet)
		{
			printf("Set Trigger Mode fail! nRet [0x%x]\n", nRet);
			break;
		}

		unsigned int nThreadID = 0;
		void* hThreadHandle = (void*)_beginthreadex(NULL, 0, WorkThread, handle, 0, &nThreadID);
		if (NULL == hThreadHandle)
		{
			break;
		}

		GetExposureLimits(handle, minExposure, maxExposure);
		GetGainLimits(handle, minGain, maxGain);

		if (maxExposure >= maxAllowedExposure) maxExposure = maxAllowedExposure;

		nRet = MV_CC_StartGrabbing(handle);
		if (MV_OK != nRet)
		{
			printf("Start Grabbing fail! nRet [0x%x]\n", nRet);
			break;
		}

		printf("Press a key to stop grabbing.\n");
		WaitForKeyPress();

		g_bExit = true;
		WaitForSingleObject(hThreadHandle, INFINITE);
		CloseHandle(hThreadHandle);

		nRet = MV_CC_StopGrabbing(handle);
		if (MV_OK != nRet)
		{
			printf("Stop Grabbing fail! nRet [0x%x]\n", nRet);
			break;
		}

		nRet = MV_CC_CloseDevice(handle);
		if (MV_OK != nRet)
		{
			printf("ClosDevice fail! nRet [0x%x]\n", nRet);
			break;
		}

		nRet = MV_CC_DestroyHandle(handle);
		if (MV_OK != nRet)
		{
			printf("Destroy Handle fail! nRet [0x%x]\n", nRet);
			break;
		}
		handle = NULL;
	} while (0);

	if (handle != NULL)
	{
		MV_CC_DestroyHandle(handle);
		handle = NULL;
	}

	MV_CC_Finalize();

	printf("Press a key to exit.\n");
	WaitForKeyPress();

	return 0;
}
