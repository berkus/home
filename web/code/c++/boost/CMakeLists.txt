project(tryboost)
find_package(Boost COMPONENTS system thread)

if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS})
endif()

set(FEATURES executor)

foreach(feature ${FEATURES})
  add_executable(${feature} ${feature}.cpp)
  target_link_libraries(${feature} ${Boost_LIBRARIES})
  add_test(${feature}_test ${feature})
endforeach()
