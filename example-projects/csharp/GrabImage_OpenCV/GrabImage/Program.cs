using System;
using MvCamCtrl.NET;
using System.Runtime.InteropServices;
using System.Threading;
using OpenCvSharp;
using System.Diagnostics;

namespace GrabImage
{
    class GrabImage
    {
        static bool g_bExit = false;
        static int count = 0;
        static double sum = 0.0;
        static int maxAllowedExposure = 1000000;

        static int minExposure = 1000; // Set this to your camera's minimum exposure value
        static int maxExposure = 500000; // Set this to your camera's maximum exposure value
        static int minGain = 0; // Set this to your camera's minimum gain value
        static int maxGain = 100; // Set this to your camera's maximum gain value


        public static void ReceiveImageWorkThread(object obj)
        {
            int nRet = MyCamera.MV_OK;
            MyCamera device = obj as MyCamera;
            MyCamera.MV_FRAME_OUT stImageOut = new MyCamera.MV_FRAME_OUT();

            // Create a window to display the image
            string windowName = "Camera Feed";
            Cv2.NamedWindow(windowName);

            // Create a window for trackbars
            string settingsWindow = "Settings";
            Cv2.NamedWindow(settingsWindow);

            // Create trackbars for exposure and gain


            // Create trackbars for exposure and gain
            Cv2.CreateTrackbar("Exposure", settingsWindow, ref minExposure, maxExposure, null);
            Cv2.CreateTrackbar("Gain", settingsWindow, ref minGain, maxGain, null);

            while (true)
            {
                nRet = device.MV_CC_GetImageBuffer_NET(ref stImageOut, 1000);
                if (nRet == MyCamera.MV_OK)
                {
                    try
                    {
                        int width = stImageOut.stFrameInfo.nWidth;
                        int height = stImageOut.stFrameInfo.nHeight;
                        int dataSize = (int)stImageOut.stFrameInfo.nFrameLen;

                        Stopwatch stopwatch = new Stopwatch();
                        stopwatch.Start();

                        // Create a byte array to hold the image data
                        byte[] imageData = new byte[dataSize];
                        Marshal.Copy(stImageOut.pBufAddr, imageData, 0, dataSize);

                        // Create Mat for the raw data
                        using (Mat rawImg = new Mat(height, width, MatType.CV_8UC1))
                        {
                            Marshal.Copy(imageData, 0, rawImg.Data, dataSize);

                            using (Mat colorImg = new Mat())
                            {
                                // Convert from Bayer BG to BGR
                                Cv2.CvtColor(rawImg, colorImg, ColorConversionCodes.BayerBG2BGR);

                                // Display the image with correct colors
                                Cv2.ImShow(windowName, colorImg);
                            }

                            stopwatch.Stop();
                            TimeSpan elapsedTime = stopwatch.Elapsed;
                            count++;

                            if (count < 1000)
                                sum += elapsedTime.TotalSeconds;
                            else if (count == 1000)
                                Console.WriteLine("Average color convertion time: " + sum / 1000 + " seconds");

                            

                            // Wait for 1ms to process GUI events
                            int key = Cv2.WaitKey(1);
                            if (key == 27) // ESC key
                            {
                                g_bExit = true;
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error processing image: {ex.Message}");
                    }
                    finally
                    {
                        device.MV_CC_FreeImageBuffer_NET(ref stImageOut);
                    }
                }
                else
                {
                    Console.WriteLine("Get Image failed:{0:x8}", nRet);
                }
                if (g_bExit)
                {
                    break;
                }

                // Get trackbar positions
                int exposure = Cv2.GetTrackbarPos("Exposure", settingsWindow);
                int gain = Cv2.GetTrackbarPos("Gain", settingsWindow);

                // Set camera parameters
                device.MV_CC_SetFloatValue_NET("ExposureTime", (float)exposure);
                device.MV_CC_SetFloatValue_NET("Gain", (float)gain);
            }

            // Clean up
            Cv2.DestroyWindow(windowName);
            Cv2.DestroyWindow(settingsWindow);
        }


        

        static void Main(string[] args)
        {
            int nRet = MyCamera.MV_OK;

            // Initialize SDK
            MyCamera.MV_CC_Initialize_NET();

            MyCamera device = new MyCamera();
            do
            {
                // Enum device
                MyCamera.MV_CC_DEVICE_INFO_LIST stDevList = new MyCamera.MV_CC_DEVICE_INFO_LIST();
                nRet = MyCamera.MV_CC_EnumDevices_NET(MyCamera.MV_GIGE_DEVICE | MyCamera.MV_USB_DEVICE, ref stDevList);
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Enum device failed:{0:x8}", nRet);
                    break;
                }
                Console.WriteLine("Enum device count : " + Convert.ToString(stDevList.nDeviceNum));
                if (0 == stDevList.nDeviceNum)
                {
                    break;
                }

                MyCamera.MV_CC_DEVICE_INFO stDevInfo;

                // Print device info
                for (Int32 i = 0; i < stDevList.nDeviceNum; i++)
                {
                    stDevInfo = (MyCamera.MV_CC_DEVICE_INFO)Marshal.PtrToStructure(stDevList.pDeviceInfo[i], typeof(MyCamera.MV_CC_DEVICE_INFO));

                    if (MyCamera.MV_GIGE_DEVICE == stDevInfo.nTLayerType)
                    {
                        MyCamera.MV_GIGE_DEVICE_INFO_EX stGigEDeviceInfo = (MyCamera.MV_GIGE_DEVICE_INFO_EX)MyCamera.ByteToStruct(stDevInfo.SpecialInfo.stGigEInfo, typeof(MyCamera.MV_GIGE_DEVICE_INFO_EX));
                        uint nIp1 = ((stGigEDeviceInfo.nCurrentIp & 0xff000000) >> 24);
                        uint nIp2 = ((stGigEDeviceInfo.nCurrentIp & 0x00ff0000) >> 16);
                        uint nIp3 = ((stGigEDeviceInfo.nCurrentIp & 0x0000ff00) >> 8);
                        uint nIp4 = (stGigEDeviceInfo.nCurrentIp & 0x000000ff);
                        Console.WriteLine("[device " + i.ToString() + "]:");
                        Console.WriteLine("DevIP:" + nIp1 + "." + nIp2 + "." + nIp3 + "." + nIp4);
                        Console.WriteLine("ModelName:" + stGigEDeviceInfo.chModelName + "\n");
                    }
                    else if (MyCamera.MV_USB_DEVICE == stDevInfo.nTLayerType)
                    {
                        MyCamera.MV_USB3_DEVICE_INFO_EX stUsb3DeviceInfo = (MyCamera.MV_USB3_DEVICE_INFO_EX)MyCamera.ByteToStruct(stDevInfo.SpecialInfo.stUsb3VInfo, typeof(MyCamera.MV_USB3_DEVICE_INFO_EX));
                        Console.WriteLine("[device " + i.ToString() + "]:");
                        Console.WriteLine("SerialNumber:" + stUsb3DeviceInfo.chSerialNumber);
                        Console.WriteLine("ModelName:" + stUsb3DeviceInfo.chModelName + "\n");
                    }
                }

                Int32 nDevIndex = 0;
                Console.Write("Please input index(0-{0:d}):", stDevList.nDeviceNum - 1);
                try
                {
                    nDevIndex = Convert.ToInt32(Console.ReadLine());
                }
                catch
                {
                    Console.Write("Invalid Input!\n");
                    break;
                }

                if (nDevIndex > stDevList.nDeviceNum - 1 || nDevIndex < 0)
                {
                    Console.Write("Input Error!\n");
                    break;
                }
                stDevInfo = (MyCamera.MV_CC_DEVICE_INFO)Marshal.PtrToStructure(stDevList.pDeviceInfo[nDevIndex], typeof(MyCamera.MV_CC_DEVICE_INFO));

                // Create device
                nRet = device.MV_CC_CreateDevice_NET(ref stDevInfo);
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Create device failed:{0:x8}", nRet);
                    break;
                }

                // Open device
                nRet = device.MV_CC_OpenDevice_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Open device failed:{0:x8}", nRet);
                    break;
                }

                // Detection network optimal package size(It only works for the GigE camera)
                if (stDevInfo.nTLayerType == MyCamera.MV_GIGE_DEVICE)
                {
                    int nPacketSize = device.MV_CC_GetOptimalPacketSize_NET();
                    if (nPacketSize > 0)
                    {
                        nRet = device.MV_CC_SetIntValueEx_NET("GevSCPSPacketSize", nPacketSize);
                        if (nRet != MyCamera.MV_OK)
                        {
                            Console.WriteLine("Warning: Set Packet Size failed {0:x8}", nRet);
                        }
                    }
                    else
                    {
                        Console.WriteLine("Warning: Get Packet Size failed {0:x8}", nPacketSize);
                    }
                }

                // set trigger mode as off
                if (MyCamera.MV_OK != device.MV_CC_SetEnumValue_NET("TriggerMode", 0))
                {
                    Console.WriteLine("Set TriggerMode failed:{0:x8}", nRet);
                    break;
                }

                // start grab
                nRet = device.MV_CC_StartGrabbing_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Start grabbing failed:{0:x8}", nRet);
                    break;
                }

                // Get exposure and gain limits from the camera
                MyCamera.MVCC_FLOATVALUE exposureLimits = new MyCamera.MVCC_FLOATVALUE();
                MyCamera.MVCC_FLOATVALUE gainLimits = new MyCamera.MVCC_FLOATVALUE();

                device.MV_CC_GetFloatValue_NET("ExposureTime", ref exposureLimits);
                device.MV_CC_GetFloatValue_NET("Gain", ref gainLimits);

                // Variables to hold current trackbar positions
                int currentExposure = (int)exposureLimits.fCurValue;
                int currentGain = (int)gainLimits.fCurValue;

                maxExposure = (int)exposureLimits.fMax;
                if (maxExposure >= maxAllowedExposure)
                {
                    maxExposure = maxAllowedExposure;
                }
                maxGain = (int)gainLimits.fMax;
                minExposure = (int)exposureLimits.fMin;
                minGain = (int)gainLimits.fMin;
      


                Thread hReceiveImageThreadHandle = new Thread(ReceiveImageWorkThread);
                hReceiveImageThreadHandle.Start(device);

                Console.WriteLine("Press enter to exit");
                Console.ReadKey();

                g_bExit = true;
                Thread.Sleep(1000);

                // Stop grab image
                nRet = device.MV_CC_StopGrabbing_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Stop grabbing failed:{0:x8}", nRet);
                    break;
                }

                // Close device
                nRet = device.MV_CC_CloseDevice_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Close device failed:{0:x8}", nRet);
                    break;
                }

                // Destroy device
                nRet = device.MV_CC_DestroyDevice_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Destroy device failed:{0:x8}", nRet);
                    break;
                }
            } while (false);

            if (MyCamera.MV_OK != nRet)
            {
                // Destroy device
                nRet = device.MV_CC_DestroyDevice_NET();
                if (MyCamera.MV_OK != nRet)
                {
                    Console.WriteLine("Destroy device failed:{0:x8}", nRet);
                }
            }

            // Finalize SDK
            MyCamera.MV_CC_Finalize_NET();
        }
    }
}
