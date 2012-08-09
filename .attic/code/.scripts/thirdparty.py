# -*- coding: utf-8 -*-


def UseThirdParty(env, name, libs=[]):
    env.Append(CPPPATH=_include(name))
    env.Append(LIBPATH=_libpath(name))
    env.Append(LIBS=_libs(name) + libs)
    env.Append(CPPDEFINES=_defines(name))


def _include(name):
    return _database[name]['INCLUDE']


def _libpath(name):
    return _database[name]['LIBPATH']


def _libs(name):
    return _database[name]['LIBS']


def _defines(name):
    return _database[name]['CPPDEFINES']


_database = {'GTEST': {
    'INCLUDE': '$REPOSITORY/gtest/include',
    'LIBPATH': '$REPOSITORY/gtest/$PLATFORM/lib',
    'LIBS': ['gtest$DEBUGSUFFIX', 'gtest_main$DEBUGSUFFIX'],
    'CPPDEFINES': [''],
    }, 'BOOST': {
    'INCLUDE': '$REPOSITORY/boost/include',
    'LIBPATH': '$REPOSITORY/boost/$PLATFORM/lib',
    'LIBS': [],
    'CPPDEFINES': [''],
    }, 'PROTOBUF': {
    'INCLUDE': '$REPOSITORY/protobuf/include',
    'LIBPATH': '$REPOSITORY/protobuf/$VARIANT/lib',
    'LIBS': ['libprotobuf'],
    'CPPDEFINES': [''],
    }}
