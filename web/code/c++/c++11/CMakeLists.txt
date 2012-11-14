PROJECT(C++11)
SET(CMAKE_CXX_FLAGS "--std=c++11")
SET(FEATURES langsupport)

FOREACH(feature ${FEATURES})
  ADD_EXECUTABLE(${feature} ${feature}.cpp)
  TARGET_LINK_LIBRARIES(${feature})
  ADD_TEST(${feature}_test ${feature})
ENDFOREACH()
