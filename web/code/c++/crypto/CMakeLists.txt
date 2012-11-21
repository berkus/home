project(crypto)
find_package(OpenSSL)

enable_cpp11()

if(OPENSSL_FOUND)
  include_directories(${OPENSSL_INCLUDE_DIR})
endif()

add_executable(crypto crypto.cpp)
target_link_libraries(crypto ${OPENSSL_LIBRARIES})
add_test(crypto_test crypto)
