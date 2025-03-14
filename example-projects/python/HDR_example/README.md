# HDR Example

## 1️⃣ Project Overview
HDR Example is a real-time image acquisition and processing project that integrates Hikrobot cameras with MvCamera SDK and OpenCV. The system captures frames in HDR format (that is, different exposure levels for each image), converts them from Bayer to RGB, and displays them in an OpenCV window, providing a flexible and efficient solution for visualization.

Key Features:

1)  **Seamless Camera Integration** – Captures frames from Hikrobot cameras using the MvCamera SDK.
2)  **Real-Time Image Processing** – Converts Bayer images to OpenCV Mat format and applies processing functions.
3)  **Multi-Threaded Frame Acquisition** – Efficient, optimized frame handling for smooth performance.
4)  **Live Display** – Processed frames are resized and shown in an OpenCV window.

Expected Outcomes:

1) Real-time display of resized frames of varying exposure (that can be combined in post processing).
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
-  **Programming Language:** Python (Version: 3.13.1)
-  **Libraries:** OpenCV (Version: 4.11.0.86), NumPy (Version: 2.2.2)
-  **SDK:** Hikrobot MVS SDK (Version: 4.4.1.3)
- **IDE:** Visual Studio Code (Version: 1.98.0)


## 3️⃣ Installation and Running Instructions 

### Step 1: Install dependencies

First, install the necessary Python libraries:

```bash
pip install opencv-python numpy
```
Additionally, ensure that the Hikrobot SDK is installed and accessible from your Python environment.

### Step 2: Run the Project
Clone or download the repository, then run the script as follows:
```bash
python HDR_example.py
```

The program will enumerate available devices and prompt you to select a device to connect. Once selected, the program will start capturing HDR frames from the chosen camera and display them in real-time.

### Step 3: Stopping the Program
Press the "esc" key to stop the frame capture and close the application.


