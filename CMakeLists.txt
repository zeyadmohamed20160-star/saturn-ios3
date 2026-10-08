cmake_minimum_required(VERSION 3.15)
project(SaturnIOS3 C CXX)

# This automatically finds all your .c, .cpp, and .h files
file(GLOB_RECURSE SOURCES 
    "*.c" 
    "*.cpp" 
    "*.h" 
    "*.hpp"
)

# This groups them into an executable target
add_executable(SaturnIOS3 ${SOURCES})
