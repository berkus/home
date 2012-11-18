Date: 17/11/2011
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of a C++ wrapper around the OpenSSL
[crypto library][openssl]. The wrapper is meant to be a convenience for a developer (i.e. me) to
plug in the most common cryptographic primitives into application without having to deal with the
nuances of OpenSSL. The wrapper

#### Cryptographically Secure Random Number Generators

The first thing we need is a pseudo random number generator.




[openssl]: http://www.openssl.org/docs/crypto/crypto.html
