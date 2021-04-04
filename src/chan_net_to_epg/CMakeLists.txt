cmake_minimum_required(VERSION 3.10)
project(chan_net_to_epg)
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

set(ALL_LIBS  
    utils
    SimpleAmqpClient 
    rabbitmq
    ${Boost_LIBRARIES} 
    ${GSTMM_LIBRARIES} 
    )
set(ALL_INCS  ${GSTMM_INCLUDE_DIRS})

add_executable(${PROJECT_NAME} 
    src/${PROJECT_NAME}.cpp 
    src/${PROJECT_NAME}_gst.cpp
    )
target_link_libraries(${PROJECT_NAME}  ${ALL_LIBS})
target_include_directories(${PROJECT_NAME} PUBLIC ${ALL_INCS})

add_custom_target(copy ALL 
    COMMAND cp -f ${PROJECT_NAME} /opt/catchuptv/bin
    COMMENT "Copy to /opt/catchuptv/bin"
    DEPENDS ${PROJECT_NAME}
    )
