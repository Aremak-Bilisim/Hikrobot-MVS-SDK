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

        static MyCamera.MvGvspPixelType mvGvspPixelType;




        public static Mat ConvertPixelFormat(IntPtr buffer, MyCamera.MvGvspPixelType pixelFormat, int width, int height)
        {
            Mat image = new Mat();

            switch (pixelFormat)
            {
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono8:
                    Console.WriteLine("Mono8");
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC1, buffer);
                    Cv2.CvtColor(image, image, ColorConversionCodes.GRAY2BGR);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono10:
                    Mat img10 = Mat.FromPixelData(height, width, MatType.CV_16UC1, buffer);
                    img10.ConvertTo(img10, MatType.CV_8U, 1.0 / 4); // Scale down from 10-bit to 8-bit
                    Cv2.CvtColor(img10, image, ColorConversionCodes.GRAY2BGR);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono12:
                    Mat img12 = Mat.FromPixelData(height, width, MatType.CV_16UC1, buffer);
                    img12.ConvertTo(img12, MatType.CV_8U, 1.0 / 16); // Scale down from 12-bit to 8-bit
                    Cv2.CvtColor(img12, image, ColorConversionCodes.GRAY2BGR);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_RGB8_Packed:
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC3, buffer);
                    Cv2.CvtColor(image, image, ColorConversionCodes.RGB2BGR);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BGR8_Packed:
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC3, buffer);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_YUV422_Packed:
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC2, buffer);
                    Cv2.CvtColor(image, image, ColorConversionCodes.YUV2BGR_UYVY);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_YUV422_YUYV_Packed:
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC2, buffer);
                    Cv2.CvtColor(image, image, ColorConversionCodes.YUV2BGR_YUYV);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG8:
                    image = Mat.FromPixelData(height, width, MatType.CV_8UC1, buffer);
                    Cv2.CvtColor(image, image, ColorConversionCodes.BayerRG2RGB);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG10:
                    Mat img11 = Mat.FromPixelData(height, width, MatType.CV_16UC1, buffer);
                    img11.ConvertTo(img11, MatType.CV_8U, 1.0 / 4); // Scale down from 10-bit to 8-bit
                    Cv2.CvtColor(img11, image, ColorConversionCodes.BayerRG2RGB);
                    break;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG12:
                    Mat img13 = Mat.FromPixelData(height, width, MatType.CV_16UC1, buffer);
                    img13.ConvertTo(img13, MatType.CV_8U, 1.0 / 4); // Scale down from 10-bit to 8-bit
                    Cv2.CvtColor(img13, image, ColorConversionCodes.BayerRG2RGB);
                    break;

                default:
                    throw new Exception("Unsupported pixel format");
            }

            return image;
        }


        

        private static MatType GetMatType(MyCamera.MvGvspPixelType pixelFormat)
        {
            switch (pixelFormat)
            {
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono8:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG8:
                    return MatType.CV_8UC1;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono10:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_Mono12:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG10:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BayerRG12:
                    return MatType.CV_16UC1;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_RGB8_Packed:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_BGR8_Packed:
                    return MatType.CV_8UC3;

                case MyCamera.MvGvspPixelType.PixelType_Gvsp_YUV422_Packed:
                case MyCamera.MvGvspPixelType.PixelType_Gvsp_YUV422_YUYV_Packed:
                    return MatType.CV_8UC2;

            
                default:
                    throw new Exception("Unsupported pixel format");
            }
        }


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

                        mvGvspPixelType = stImageOut.stFrameInfo.enPixelType;
                        Console.WriteLine($"Image Format: {mvGvspPixelType}");

                        Stopwatch stopwatch = new Stopwatch();
                        stopwatch.Start();

                        // Create a byte array to hold the image data
                        byte[] imageData = new byte[dataSize];
                        Marshal.Copy(stImageOut.pBufAddr, imageData, 0, dataSize);

                        // Create Mat for the raw data
                        using (Mat rawImg = new Mat(height, width, GetMatType(mvGvspPixelType)))
                        {
                            Marshal.Copy(imageData, 0, rawImg.Data, dataSize);

                            // Call ConvertPixelFormat function
                            Mat colorImg = ConvertPixelFormat(stImageOut.pBufAddr, mvGvspPixelType, width, height);


                            // Display the image with correct colors
                            Cv2.ImShow(windowName, colorImg);

                            stopwatch.Stop();
                            TimeSpan elapsedTime = stopwatch.Elapsed;
                            count++;

                            if (count < 1000)
                                sum += elapsedTime.TotalSeconds;
                            else if (count == 1000)
                                Console.WriteLine("Average color conversion time: " + sum / 1000 + " seconds");

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
                Console.Write("Please input index(0-{0:d}): ", stDevList.nDeviceNum - 1);
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
