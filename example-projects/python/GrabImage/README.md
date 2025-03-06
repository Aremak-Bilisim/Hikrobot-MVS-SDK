# Grab Image

## 1️⃣ Project Overview
This project captures frames from a camera using the MvCamera SDK, processes them (converts from Bayer to RGB), and displays the resized frames in a window. The purpose of this project is to demonstrate real-time image capture and processing from supported camera devices, allowing users to easily visualize the captured frames.

Key Objectives:

1) Capture and process frames from cameras using the MvCamera SDK.
2) Display the captured images in real-time with OpenCV.
3) Implement camera configuration options like Gain and Exposure Time.

Expected Outcomes:

1) Real-time display of resized frames.
2) Seamless capture and processing of images in various formats.
3) Flexible and multi-threaded frame acquisition and display.


## 2️⃣ Software Used

- **Operating System:** Windows/Linux
- **Software Tools:** 
  - Python
  - OpenCV
  - Hikrobot SDK (MvCamera SDK)
  - NumPy

## 3️⃣ Installation and Running Instructions 🚀

### Step 1: Install dependencies

First, install the necessary Python libraries:

```bash
pip install opencv-python numpy
```
Additionally, ensure that the Hikrobot SDK is installed and accessible from your Python environment.

### Step 2: Run the Project
Clone or download the repository, then run the script as follows:
```bash
python GrabImage_OpenCV.py
```

The program will enumerate available devices and prompt you to select a device to connect. Once selected, the program will start capturing frames from the chosen camera and display them in real-time.

### Step 3: Stopping the Program
Press any key to stop the frame capture and close the application.


