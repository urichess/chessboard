cmake_minimum_required(VERSION 3.20.0)

# Initialize Zephyr
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(chessboard_zephyr)

# Include sources
target_sources(app PRIVATE src/main.cpp src/Led.cpp src/utils.cpp src/SensorsMatrix.cpp src/UartSender.cpp src/FlashStorage.cpp)

# Optional: Set additional compile options if needed
# e.g., add compile options or flags here if necessary
#target_compile_options(app PRIVATE -g -O0)  # Debugging symbols and no optimization


