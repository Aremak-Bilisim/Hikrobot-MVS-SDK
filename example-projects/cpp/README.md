# C++ Project Setup in Visual Studio 2015

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)

## Introduction

This guide will help you set up your development environment, run the provided C++ file, and get started with contributing to the project.

## Prerequisites

Before you begin, ensure you have the following installed on your PC:

- Visual Studio 2015 (or a compatible version)
- OpenCV 4.11.0 (or a compatible version)

## Installation

Provide step-by-step instructions for installing Visual Studio 2015 and any additional tools or libraries required for the project.

## Project Setup

1. **Add OpenCV to System Path:**

   - Add `\PATH_TO_OPENCV\opencv\build\x64\vcXX\bin` to your System Path environment variable. This ensures that the OpenCV DLLs are accessible to your project.

2. **Configure Visual Studio 2015:**

   - Open your project in Visual Studio 2015.
   - In the Solution Explorer, right-click on the `GrabImage` project and select "Properties."

3. **Configure Include Directories:**

   - Navigate to `C/C++ -> General -> Additional Include Directories`.
   - Add `PATH_TO_OPENCV\opencv\build\include` to the list. This allows the compiler to locate the OpenCV header files.

4. **Configure Library Directories:**

   - Navigate to `Linker -> General -> Additional Library Directories`.
   - Add `PATH_TO_OPENCV\opencv\build\x64\vcXX\lib` to the list. This allows the linker to locate the OpenCV library files.

5. **Configure Additional Dependencies:**

   - Navigate to `Linker -> Input -> Additional Dependencies`.
   - Add `opencv_worldXXXX.lib` to the list. This file is located in `PATH_TO_OPENCV\opencv\build\x64\vcXX\lib`.

6. **Repeat for Both Configurations:**
   - Ensure that the above steps are performed for both the `Debug` and `Release` configurations.

By following these steps, you will have successfully set up your Visual Studio 2015 project to use OpenCV. Run the project using Visual Studio 2015 and enjoy!
