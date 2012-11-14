C++ Standard Library: Language Support

This page describes the parts of the C++ standard library that deal with runtime language
support. This includes support for things like data type limits, start and termination hooks,
dynamic memory management, dynamic type inference, etc.

The C header is carried into C++ with a few extensions. It brings in some esoteric C-style types and
macros which can be used to scare small children. Take for instance `offsetof` which can be used to
obtain the offset of members inside PODs.

[container_of]: http://www.kroah.com/log/linux/container_of.html
