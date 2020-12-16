# Qt Widgets for Technical Applications
# available at http://qwt.sourceforge.net/
#
# The module defines the following variables:
#  Qwt_FOUND - the system has Qwt
#  Qwt_INCLUDE_DIR - where to find qwt_plot.h
#  Qwt_INCLUDE_DIRS - qwt includes
#  Qwt_Qwt_LIBRARY - where to find the Qwt library
#  Qwt_Mathml_LIBRARY - where to find Mathml library
#  Qwt_LIBRARIES - aditional libraries need to be linked
#  Qwt_MAJOR_VERSION - major version
#  Qwt_MINOR_VERSION - minor version
#  Qwt_PATCH_VERSION - patch version
#  Qwt_VERSION_STRING - version (ex. 5.2.1)
#  Qwt_ROOT_DIR - root directory of Qwt installation

set(Qwt_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR})

find_path(Qwt_INCLUDE_DIR NAMES qwt_plot.h PATHS "${CMAKE_CURRENT_LIST_DIR}/include")

set(Qwt_INCLUDE_DIRS ${Qwt_INCLUDE_DIR})

#-------------------------------- Extract version --------------------------------------------------

set(_VERSION_FILE ${Qwt_INCLUDE_DIR}/qwt_global.h)
if(EXISTS ${_VERSION_FILE})
    file(STRINGS ${_VERSION_FILE} _VERSION_LINE REGEX "define[ ]+QWT_VERSION_STR")
    if(_VERSION_LINE)
        string (REGEX REPLACE ".*define[ ]+QWT_VERSION_STR[ ]+\"(.*)\".*" "\\1" QWT_VERSION_STRING "${_VERSION_LINE}")
        string (REGEX REPLACE "([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\1" Qwt_MAJOR_VERSION "${QWT_VERSION_STRING}")
        string (REGEX REPLACE "([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\2" Qwt_MINOR_VERSION "${QWT_VERSION_STRING}")
        string (REGEX REPLACE "([0-9]+)\\.([0-9]+)\\.([0-9]+)" "\\3" Qwt_PATCH_VERSION "${QWT_VERSION_STRING}")
    endif()
endif()

#-------------------------------- Check version ----------------------------------------------------

set(_QWT_VERSION_MATCH TRUE)
if(Qwt_FIND_VERSION AND QWT_VERSION_STRING)
    if(Qwt_FIND_VERSION_EXACT)
        if(NOT Qwt_FIND_VERSION VERSION_EQUAL QWT_VERSION_STRING)
            set(_QWT_VERSION_MATCH FALSE)
        endif()
    else()
        if(QWT_VERSION_STRING VERSION_LESS Qwt_FIND_VERSION)
            set(_QWT_VERSION_MATCH FALSE)
        endif()
    endif()
endif()

#-------------------------------- Find library files -----------------------------------------------

find_library(Qwt_Qwt_LIBRARY 
  NAMES qwt 
  PATHS "${CMAKE_CURRENT_LIST_DIR}"
  PATH_SUFFIXES lib
  NO_DEFAULT_PATH
)

find_library(Qwt_Mathml_LIBRARY 
  NAMES qwtmathml 
  PATHS "${CMAKE_CURRENT_LIST_DIR}"
  PATH_SUFFIXES lib
  NO_DEFAULT_PATH
)

#-------------------------------- Set component status ---------------------------------------------

if(NOT "${Qwt_FIND_COMPONENTS}")
    # Add default component
    set("${Qwt_FIND_COMPONENTS}" "Qwt")
endif()

set(_qwt_component_required_vars)

foreach(_comp ${Qwt_FIND_COMPONENTS})
    if ("${_comp}" STREQUAL "Qwt")
        list(APPEND _qwt_component_required_vars ${Qwt_Qwt_LIBRARY})
        if (Qwt_INCLUDE_DIR AND EXISTS "${Qwt_Qwt_LIBRARY}")
            set(Qwt_Qwt_FOUND TRUE)
        else()
            set(Qwt_Qwt_FOUND False)
        endif()
        
    elseif("${_comp}" STREQUAL "Mathml")
        list(APPEND _qwt_component_required_vars ${Qwt_Mathml_LIBRARY})
        if (Qwt_INCLUDE_DIR AND EXISTS "${Qwt_Qwt_LIBRARY}" AND EXISTS "${Qwt_Mathml_LIBRARY}")
            set(Qwt_Mathml_FOUND TRUE)
        else()
            set(Qwt_Mathml_FOUND False)
        endif()    
    
    else()
        message(WARNING "${_comp} is not a recognized Qwt component")
        set(Qwt_${_comp}_FOUND FALSE)
    endif()
endforeach()

#-------------------------------- Handle find_package() arguments ----------------------------------

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Qwt
    REQUIRED_VARS _qwt_component_required_vars
    VERSION_VAR QWT_VERSION_STRING
    HANDLE_COMPONENTS
)

#-------------------------------- Export found libraries as imported targets -----------------------

set(Qwt_LIBRARIES "Qt5::Core;Qt5::Concurrent;Qt5::PrintSupport;Qt5::OpenGL")
list(APPEND Qwt_LIBRARIES "Qt5::Svg")

if(Qwt_Qwt_FOUND AND NOT TARGET Qwt::Qwt)
    add_library(Qwt::Qwt STATIC IMPORTED)
    set_target_properties(Qwt::Qwt PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${Qwt_INCLUDE_DIRS}"
        INTERFACE_LINK_LIBRARIES "${Qwt_LIBRARIES}"
        IMPORTED_LOCATION "${Qwt_Qwt_LIBRARY}"
    )
    
endif()

if(Qwt_Mathml_FOUND AND NOT TARGET Qwt::Mathml)
    add_library(Qwt::Mathml STATIC IMPORTED)
    set_target_properties(Qwt::Qwt PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${Qwt_INCLUDE_DIRS}"
        INTERFACE_LINK_LIBRARIES "${Qwt_Qwt_LIBRARY};${Qwt_LIBRARIES}"
        IMPORTED_LOCATION "${Qwt_Mathml_LIBRARY}"
    )
endif()
