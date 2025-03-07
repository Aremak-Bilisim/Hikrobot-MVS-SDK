# GrabImage_OpenCV

## 1️⃣ Project Overview
GrabImage_OpenCV is a real-time image acquisition and processing project that integrates Hikrobot cameras with MvCamera SDK and OpenCV. The system captures frames, converts them from Bayer to RGB, and displays them in an OpenCV window, providing a flexible and efficient solution for visualization.

### Key Features:

- **Seamless Camera Integration** – Captures frames from Hikrobot cameras using the MvCamera SDK.
- **Real-Time Image Processing** – Converts Bayer images to OpenCV Mat format and applies color transformation.
- **Multi-Threaded Frame Acquisition** – Efficient, optimized frame handling for smooth performance.
- **Live Display** – Processed frames are resized and shown in an OpenCV window.

### Expected Outcomes:
- Real-time display of resized frames.
- Seamless capture and processing of images in Bayer format.
- Efficient and multi-threaded frame acquisition and display.

## 2️⃣ Equipment and Technologies Used

### Hardware Components:
- **Camera Model:** Hikrobot MV-CA023-10UC
- **Lens:** MVL-HF0828M-6MPE
- **Camera Stand:** Aremak Adjustable Machine Vision Test Stand
- **Lighting:** Hikrobot Shadowless Ring Light(MV-LGES-116-W)

### Software Tools:
- **Operating System:** Windows 10/11
- **Programming Language:** C#
- **Libraries:** OpenCV (Version: 4.11.0)
- **SDK:** Hikrobot MVS SDK (Version: 4.4.1.3)
- **Build Tools:** Microsoft Visual Studio 2015

## 3️⃣ Installation and Setup

### Prerequisites:
1. Install **MvCamera SDK** and ensure drivers are properly set up.
2. Install **OpenCV** for image processing.
3. Install .NET Framework 4.8 Developer Pack if you don't have it
4. Set up a development environment with **Visual Studio**.

### Compilation Instructions:
1. Clone or download the source code.
2. Open the project in Visual Studio.
3. Link **MvCamera SDK** and **OpenCV** libraries.
4. Compile and build the project.

## 4️⃣ How It Works

1. **Initialize SDK** - The program initializes the MvCamera SDK and enumerates connected devices.
2. **Device Selection** - The user selects a camera from the detected list.
3. **Camera Configuration** - The selected camera is opened, and trigger mode is set to continuous.
4. **Frame Acquisition** - The camera continuously captures frames and passes them to a separate thread for processing.
5. **Image Processing** - The raw Bayer image is converted to RGB, resized, and displayed in an OpenCV window.
6. **User Interaction** - The program listens for the 'Esc' key to stop acquisition and safely close the camera.

## 5️⃣ Usage Instructions

1. Run the executable after building the project.
2. Select the camera index from the listed devices.
3. The captured frames will be displayed in an OpenCV window.
4. Press **Esc** to exit and properly release resources.
