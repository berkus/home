project(tryboost)
enable_boost_libraries(system thread)

set(FEATURES executor)

foreach(feature ${FEATURES})
  add_executable(${feature} ${feature}.cpp)
  target_link_libraries(${feature} ${Boost_LIBRARIES})
  add_test(${feature}_test ${feature})
endforeach()
