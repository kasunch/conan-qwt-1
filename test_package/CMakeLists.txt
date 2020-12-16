cmake_minimum_required(VERSION 3.1)

project (demo CXX)
set(CMAKE_CXX_STANDARD 11)

if(NOT SET_UP_CONFIGURATIONS_DONE)
    set(SET_UP_CONFIGURATIONS_DONE TRUE)
    # No reason to set CMAKE_CONFIGURATION_TYPES if it's not a multiconfig generator
    # Also no reason mess with CMAKE_BUILD_TYPE if it's a multiconfig generator.
    get_property(isMultiConfig GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(isMultiConfig)
        set(CMAKE_CONFIGURATION_TYPES "Debug;Release" CACHE STRING "" FORCE) 
    else()
        if(NOT CMAKE_BUILD_TYPE)
            message(STATUS "Defaulting to release build.")
            set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
        endif()
        set_property(CACHE CMAKE_BUILD_TYPE PROPERTY HELPSTRING "Choose the type of build")
        # set the valid options for cmake-gui drop-down list
        set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug;Release;Profile")
    endif()
endif()

option(USE_CONAN_BUILD_INFO "Whether or not to use conanbuildinfo.cmake file"  OFF)

if (USE_CONAN_BUILD_INFO)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
endif()

find_package(Qt5 COMPONENTS Core REQUIRED)
find_package(Qt5 COMPONENTS Gui REQUIRED)
find_package(Qt5 COMPONENTS Widgets REQUIRED)
find_package(Qt5 COMPONENTS OpenGL REQUIRED)
find_package(Qt5 COMPONENTS PrintSupport REQUIRED)
find_package(Qt5 COMPONENTS Concurrent REQUIRED)
# Qt5Svg is not built as a component of the default Qt5 build.
find_package(Qt5Svg REQUIRED)
find_package(Threads REQUIRED)
find_package(Qwt COMPONENTS Qwt REQUIRED)

if(MSVC)
    # This is a GUI application without the console
    add_executable(simpleplot WIN32 simpleplot.cpp)
else()
    add_executable(simpleplot simpleplot.cpp)
endif()

target_include_directories(simpleplot PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_include_directories(simpleplot PRIVATE ${Qt5Core_INCLUDE_DIRS})
target_include_directories(simpleplot PRIVATE ${Qwt_INCLUDE_DIRS})

target_link_libraries(simpleplot Qt5::Core)
target_link_libraries(simpleplot Qt5::Concurrent)
target_link_libraries(simpleplot Qt5::Gui)
target_link_libraries(simpleplot Qt5::Widgets)
target_link_libraries(simpleplot Qt5::OpenGL)
target_link_libraries(simpleplot Qt5::PrintSupport)
target_link_libraries(simpleplot Qt5::Svg)
target_link_libraries(simpleplot Qwt::Qwt)
target_link_libraries(simpleplot ${CMAKE_THREAD_LIBS_INIT})