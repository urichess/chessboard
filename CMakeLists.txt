cmake_minimum_required(VERSION 3.20.0)

# Initialize Zephyr
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(my_arduino_uno_r4_wifi)

# Include sources
target_sources(app PRIVATE src/main.c)

# Optional: Set additional compile options if needed
# e.g., add compile options or flags here if necessary
#target_compile_options(app PRIVATE -g -O0)  # Debugging symbols and no optimization


