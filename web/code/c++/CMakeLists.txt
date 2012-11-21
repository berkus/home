cmake_minimum_required(VERSION 2.8)

set(CMAKE_BUILD_TYPE "Debug")

project(web)

macro(enable_cpp11)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++11")
  if(APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --stdlib=libc++")
  endif()
endmacro()

enable_testing()

add_subdirectory(boost)
add_subdirectory(c++11)
add_subdirectory(crypto)
