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

# Utility rule file for copy.

# Include the progress variables for this target.
include CMakeFiles/copy.dir/progress.make

CMakeFiles/copy: chan_net_to_epg
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold --progress-dir=/opt/catchuptv/src/chan-net-to-epg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Copy to /opt/catchuptv/bin"
	cp -f chan_net_to_epg /opt/catchuptv/bin

copy: CMakeFiles/copy
copy: CMakeFiles/copy.dir/build.make

.PHONY : copy

# Rule to build all files generated by this target.
CMakeFiles/copy.dir/build: copy

.PHONY : CMakeFiles/copy.dir/build

CMakeFiles/copy.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/copy.dir/cmake_clean.cmake
.PHONY : CMakeFiles/copy.dir/clean

CMakeFiles/copy.dir/depend:
	cd /opt/catchuptv/src/chan-net-to-epg && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg /opt/catchuptv/src/chan-net-to-epg/CMakeFiles/copy.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/copy.dir/depend
