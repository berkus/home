project(boost)
enable_cpp11()
add_executable(tree tree.cpp tree.h)
add_test(tree_test tree)
