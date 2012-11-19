Date: 17/11/2011
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of a C++ [wrapper][final] around the OpenSSL
[crypto][openssl] library. The idea is to go through the dense OpenSSL documentation once, implement
the most common cryptographic primitives correctly and then hide the implementation behind a C++
interface. The wrapper can then be reused across different applications without having to deal with
OpenSSL nuances.

The wrapper is header-only with the entire implementation in [`crypto.h`][final].

```` cpp
namespace ajd { namespace crypto {
  /// A typedef to represent bytes
  typedef unsigned char byte;
````

All that follows is in `ajd::crypto` namespace.

### Generating Cryptographically Secure Random Numbers

We start with pseudo random number generation. Generating cryptographically secure random numbers is
tricky and OpenSSL does that for us with its [rand][rand] methods. OpenSSL attempts to seed the PRNG
using the best source of randomness available on the platform. Depending on the platform, these
attempts may or may not succeed. The wrapper provides a hook `random_ok` to check if the OpenSSL
PRNG is sufficiently seeded. 

```` cpp
/// Checks if the underlying crypto system has seeded its PRNG sufficiently. If this method
/// returns false, you should consider using OpenSSL RAND_add to seed the PRNG.

/// _Returns_: true if the underlying PRNG is good to go.
bool random_ok() { return RAND_status() == 1; }
````

Typically, if this hook returns false, you're in bad shape, especially if you're relying on random
data to be used as encryption keys.

Assuming we have sufficient randomness to start with, the wrapper provides methods to generate an
arbitrary number of random bytes using two template methods similar to the STL `generate` and
`generate_n`. The only difference from the STL algorithms is that these do not take a generator
argument, instead these use the OpenSSL [RAND_bytes][bytes]. A alternate (simpler) implementation
could have been to just provide the random generator and let the user use the STL algorithms but
that way we end up making n calls of the `RAND_bytes` instead of one.

```` cpp
/// Algorithms for generating random bytes. The interface and implementation are the similar to
/// std::generate_random_n and std::generate_random with the generator argument fixed to OpenSSL PRNG.

/// _Effects_: generate_random invokes RAND_bytes and assigns the returned bytes through all the
/// iterators in the range [first,last). generate_random_n does the same through all the iterators in
/// the range [first,first + n) if n is positive, otherwise it does nothing.

/// _Requires_: The iterator must belong to a container of ajd::crypto::byte

/// _Returns_: generate_random_n returns `first + n`
template<typename OutputIterator, typename Size>
OutputIterator generate_random_n(OutputIterator first, Size n)
{
  typedef typename std::iterator_traits<OutputIterator>::value_type input_type;
  static_assert(std::is_same<byte, input_type>::value, "only works with bytes");

  if (n > 0)
  {
    std::vector<byte> bytes(n);
    if (RAND_bytes(&bytes[0], n) == 0)
    {
      throw std::runtime_error("random number generation failed");
    }
    first = std::copy_n(bytes.begin(), n, first);
  }
  return first;
}

template<typename ForwardIt>
void generate_random(ForwardIt first, ForwardIt last)
{
  generate_random_n(first, std::distance(first, last));
}
````

That should do for all the randomness we typically need in a general application. Here's a small
test to illustrate the usage.

```` cpp
// see if we have enough randomness.
assert(ajd::crypto::random_ok() == true);

// generate a random AES-128 key.
ajd::crypto::byte key[16];
ajd::crypto::generate_random_n(key, 16);

// generate a random 64 bit nonce.
std::vector<ajd::crypto::byte> nonce(8);
ajd::crypto::generate_random(nonce.begin(), nonce.end());

````



[rand]:http://www.openssl.org/docs/crypto/rand.html
[openssl]: http://www.openssl.org/docs/crypto/crypto.html
[bytes]: http://www.openssl.org/docs/crypto/RAND_bytes.html
[final]: https://github.com/aldrin/home/blob/master/web/code/c%2B%2B/crypto/crypto.h
