project(c++11)

SET(FEATURES thread)

foreach(feature ${FEATURES})
  add_executable(${feature} ${feature}.cpp)
  target_link_libraries(${feature})
  add_test(${feature}_test ${feature})
endforeach()
