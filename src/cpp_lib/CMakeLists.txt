cmake_minimum_required(VERSION 3.10)
project(utils)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_definitions( 
    -fdiagnostics-show-location=every-line
    -DBOOST_LOG_DYN_LINK=1
    -DGST_USE_UNSTABLE_API=1
    -Wall
    )

#BOOST
find_package(Boost COMPONENTS system log log_setup REQUIRED)

#GSTREAMER
set(CMAKE_MODULE_PATH /usr/local/lib/x86_64-linux-gnu/pkgconfig )
find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTMM REQUIRED 
    gstreamer-1.0           # for all 
    glib-2.0                # for all
    gstreamer-mpegts-1.0    # for analyse
    gstreamer-app-1.0       # for monitor
    )

set(ALL_LIBS  ${Boost_LIBRARIES} ${GSTMM_LIBRARIES})
set(ALL_INCS  ${GSTMM_INCLUDE_DIRS})
set(MYLIBS    src/utils.cpp src/gst.cpp src/mq.cpp)

add_library(${PROJECT_NAME} ${MYLIBS})
target_include_directories(utils PUBLIC ${ALL_INCS})
target_link_libraries(utils ${ALL_LIBS} )
set_target_properties(utils PROPERTIES
    IMPORTED_LOCATION "/usr/local/lib/libutils.a"
    )

add_executable(testlib src/main.cpp )
target_link_libraries(testlib utils ${ALL_LIBS} SimpleAmqpClient)
target_include_directories(testlib PUBLIC ${ALL_INCS})
