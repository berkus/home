# Copyright (c) 2013, Aldrin's Notebook.
# http://opensource.org/licenses/BSD-2-Clause

project(crypto)
find_package(OpenSSL)

enable_boost()

if(OPENSSL_FOUND)
  include_directories(${OPENSSL_INCLUDE_DIR})
endif()

add_executable(crypto crypto.cpp crypto.h)
target_link_libraries(crypto ${OPENSSL_LIBRARIES})
add_test(crypto_test crypto)

add_executable(vectors vectors.cpp crypto.h)
target_link_libraries(vectors ${OPENSSL_LIBRARIES})
add_test(vectors_test vectors)
