cmake_minimum_required(VERSION 2.8)
set(CMAKE_BUILD_TYPE "Debug")
project(web)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")

# enable c++11 features
macro(enable_cpp11)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11")
  if(APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --stdlib=libc++")
  endif()
endmacro()

# enable boost header only libraries
macro(enable_boost)
  find_package(Boost REQUIRED)
  include_directories(${Boost_INCLUDE_DIRS})
endmacro()

# enable boost libraries that need to be linked with
macro(enable_boost_libraries)
  set(Boost_USE_STATIC_LIBS ON)
  set(Boost_USE_MULTITHREADED ON)
  find_package(Boost REQUIRED COMPONENTS ${ARGV})
  include_directories(${Boost_INCLUDE_DIRS})
  if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(Boost_LIBRARIES "${Boost_LIBRARIES} -lrt")
  endif()
endmacro()

enable_testing()
add_subdirectory(boost)
add_subdirectory(c++11)
add_subdirectory(crypto)
