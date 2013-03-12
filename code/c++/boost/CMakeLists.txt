project(boost)
enable_cpp11()
enable_boost_libraries(coroutine context)

add_executable(samefringe coro_samefringe.cpp)
target_link_libraries(samefringe ${Boost_LIBRARIES})
add_test(samefringe_test samefringe)
