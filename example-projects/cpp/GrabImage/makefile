# Compiler
CXX = g++

# Compiler Flags
CXXFLAGS = -Wall -std=c++11 `pkg-config --cflags opencv4`

# Linker Flags
LDFLAGS = `pkg-config --libs opencv4` -lMvCameraControl

# Target Executable
TARGET = GrabImage

# Source Files
SRCS = GrabImage.cpp

# Object Files
OBJS = $(SRCS:.cpp=.o)

# Default Make Target
all: $(TARGET)

# Compile Source Files
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Compile Individual Object Files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean Build Files
clean:
	rm -f $(TARGET) $(OBJS)
