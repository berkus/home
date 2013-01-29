# Generates the CMake Projects
SOURCE=$(CURDIR)

# Packages I use
BOOST_HOME=$(HOME)/Packages/boost
NETLIB_HOME=$(HOME)/Packages/cpp-netlib

# CMake variables
CMAKE_VARS=-DBOOST_ROOT=$(BOOST_HOME)

# Project type
help:
	@echo "make project TYPE=<generator>"
	@echo "Supported project types: Ninja, Xcode"

project:
	rm -rf builds/$(TYPE)
	mkdir -p builds/$(TYPE)
	(cd builds/$(TYPE);	cmake -G $(TYPE) $(CMAKE_VARS) $(SOURCE))

clean:
	rm -rf builds