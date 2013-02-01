project(executors)

enable_cpp11()

add_executable(executor executor.cpp executor.h)
add_test(executor_test executor)
