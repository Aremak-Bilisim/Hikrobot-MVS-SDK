# GrabImage_OpenCV

## 1️⃣ Project Overview
GrabImage_OpenCV is a real-time image acquisition and processing project that integrates Hikrobot cameras with MvCamera SDK and OpenCV. The system captures frames, converts them from Bayer to RGB, and displays them in an OpenCV window, providing a flexible and efficient solution for visualization.

Key Features:

1)  **Seamless Camera Integration** – Captures frames from Hikrobot cameras using the MvCamera SDK.
2)  **Adjustable Camera Parameters**– Modify Gain, Exposure Time, and other settings dynamically.
3)  **Real-Time Image Processing** – Converts Bayer images to OpenCV Mat format and applies processing functions.
4)  **Multi-Threaded Frame Acquisition** – Efficient, optimized frame handling for smooth performance.
5)  **Live Display** – Processed frames are resized and shown in an OpenCV window.

Expected Outcomes:

1) Real-time display of resized frames.
2) Seamless capture and processing of images in Bayer format.
3) Flexible and multi-threaded frame acquisition and display.

## 2️⃣ Equipment and Technologies Used

### Hardware Components:
-  **Camera Model:** Hikrobot MV-CA023-10UC
-  **Lens:** MVL-HF0828M-6MPE
-  **Camera Stand:** Aremak Adjustable Machine Vision Test Stand
-  **Lighting:** Hikrobot Shadowless Ring Light(MV-LGES-116-W)

### Software Tools:
- **Operating System:** Windows 10
-  **Programming Language:** C#
-  **Libraries:** OpenCV (Version: x), .NET Framework (Version 3.5)
-  **SDK:** Hikrobot MVS SDK (Version: 4.4.1.3)
- **IDE:** Visual Studio Code (Version: 1.98.0)


## 3️⃣ Installation and Running Instructions 

### Step 1: Install dependencies
https://www.microsoft.com/en-us/download/details.aspx?id=25150
could not install 2015 VS since it is no longer supported and cant download from microsofts website. downloaded 2022.


### Step 2: Run the Project

The program will enumerate available devices and prompt you to select a device to connect. Once selected, the program will start capturing frames from the chosen camera and display them in real-time.

### Step 3: Stopping the Program
Press any key to stop the frame capture and close the application.


