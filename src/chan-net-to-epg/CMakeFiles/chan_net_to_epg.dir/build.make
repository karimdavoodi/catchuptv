# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /opt/catchuptv/src/chan-net-to-epg

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /opt/catchuptv/src/chan-net-to-epg

# Include any dependencies generated for this target.
include CMakeFiles/chan_net_to_epg.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/chan_net_to_epg.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/chan_net_to_epg.dir/flags.make

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o: CMakeFiles/chan_net_to_epg.dir/flags.make
CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o: src/chan_net_to_epg.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/opt/catchuptv/src/chan-net-to-epg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o -c /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg.cpp

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg.cpp > CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.i

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg.cpp -o CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.s

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o: CMakeFiles/chan_net_to_epg.dir/flags.make
CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o: src/chan_net_to_epg_gst.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/opt/catchuptv/src/chan-net-to-epg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o -c /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg_gst.cpp

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg_gst.cpp > CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.i

CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /opt/catchuptv/src/chan-net-to-epg/src/chan_net_to_epg_gst.cpp -o CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.s

# Object files for target chan_net_to_epg
chan_net_to_epg_OBJECTS = \
"CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o" \
"CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o"

# External object files for target chan_net_to_epg
chan_net_to_epg_EXTERNAL_OBJECTS =

chan_net_to_epg: CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg.cpp.o
chan_net_to_epg: CMakeFiles/chan_net_to_epg.dir/src/chan_net_to_epg_gst.cpp.o
chan_net_to_epg: CMakeFiles/chan_net_to_epg.dir/build.make
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_system.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_log.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_log_setup.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_log.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_chrono.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_date_time.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_filesystem.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_regex.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_thread.so.1.71.0
chan_net_to_epg: /usr/lib/x86_64-linux-gnu/libboost_atomic.so.1.71.0
chan_net_to_epg: CMakeFiles/chan_net_to_epg.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/opt/catchuptv/src/chan-net-to-epg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX executable chan_net_to_epg"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/chan_net_to_epg.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/chan_net_to_epg.dir/build: chan_net_to_epg

.PHONY : CMakeFiles/chan_net_to_epg.dir/build

CMakeFiles/chan_net_to_epg.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/chan_net_to_epg.dir/cmake_clean.cmake
.PHONY : CMakeFiles/chan_net_to_epg.dir/clean

CMakeFiles/chan_net_to_epg.dir/depend:
	cd /opt/catchuptv/src/chan-net-to-epg && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg/CMakeFiles/chan_net_to_epg.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/chan_net_to_epg.dir/depend

