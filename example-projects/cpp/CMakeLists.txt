cmake_minimum_required(VERSION 3.0)

project(GrabImage)

set(OpenCV_DIR C:/Users/Syed/Desktop/opencv/build)
find_package(OpenCV REQUIRED)

add_executable(${PROJECT_NAME} GrabImage/GrabImage.cpp)

target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})