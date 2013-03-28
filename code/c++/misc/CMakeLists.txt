# Copyright (c) 2013, Aldrin's Notebook.
# http://opensource.org/licenses/BSD-2-Clause

project(boost)
enable_cpp11()
add_executable(tree tree.cpp tree.h)
add_test(tree_test tree)
