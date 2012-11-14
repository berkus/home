PROJECT(TryBoost)

set(Boost_USE_STATIC_LIBS        ON)
FIND_PACKAGE(Boost COMPONENTS system thread unit_test_framework)
IF(Boost_FOUND)
  INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})
ENDIF()

SET(FEATURES executor)

FOREACH(feature ${FEATURES})
  ADD_EXECUTABLE(${feature} ${feature}.cpp)
  TARGET_LINK_LIBRARIES(${feature} ${Boost_LIBRARIES})
  ADD_TEST(${feature}_test ${feature})
ENDFOREACH()
