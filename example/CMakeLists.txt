cmake_minimum_required(VERSION 3.25)

# Project
project(example
    LANGUAGES CXX
    VERSION 0.1.0
    DESCRIPTION "CCPM - Custom Cmake Package Manager"
    HOMEPAGE_URL "https://github.com/byBretema/ccpm")

# Build as Debug by default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

# Target
add_executable(${PROJECT_NAME} main.cpp)

set_target_properties(${PROJECT_NAME}
    PROPERTIES
        CMAKE_CXX_EXTENSIONS OFF
        CMAKE_CXX_VISIBILITY_PRESET hidden
        CMAKE_VISIBILITY_INLINES_HIDDEN ON
        CMAKE_EXPORT_COMPILE_COMMANDS ON
)

target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)

# Dependencies
include(${CMAKE_SOURCE_DIR}/.ccpm/ccpm.cmake)

find_package(fmt REQUIRED)
find_package(glm REQUIRED)

target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt glm::glm)
