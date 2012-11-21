Date: 17/11/2011
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of a C++ [wrapper][final] around the OpenSSL
[crypto][openssl] library. Cryptography, in most applications I write, is a means to an end. These
applications usually have a "business problem" to solve and end up needing some crypto primitives


inHere
are a few expectations I have from the wrapper:

- It should be easy to use. Obviously. 
- It should be easy to integrate, preferrably header-only.
- It should hide OpenSSL from the user. It is OK to have OpenSSL on the include/link paths.

Allow me to elaborate on the first (obvious) point. Imagine you're given the task to encrypt a
configuration file. Assuming we're using a symmetric cipher, we're faced with the following
questions: algorithm should we use, AES? What should the key size be, 128 bits? What mode should the
cipher run in, CBC? For most enterprise applications (that I write for a living) the answer
generally is: "whatever works". Most applications I'm writing, crypto is a building-block, a means
to an end, and as long as we're diligent, any reasonable choice

The wrapper is header-only with the entire implementation in [`crypto.h`][final]. Everything it
contains is in the `ajd::crypto` namespace.

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

Assuming that we have sufficient randomness, the wrapper provides methods to generate an arbitrary
number of random bytes using two template methods similar to the STL `generate` and
`generate_n`. The only difference from the STL algorithms is that these do not take a generator
argument, instead these use the OpenSSL [RAND_bytes][bytes]. A alternate (simpler) implementation
could have been to just provide the random generator and let the user use the STL algorithms but
that way we end up making n calls of the `RAND_bytes` instead of one.

```` cpp
/// Algorithms for generating random bytes. The interface and implementation are the similar to
/// std::generate_random_n and std::generate_random with the generator argument fixed to OpenSSL
/// PRNG.

/// _Effects_: generate_random invokes RAND_bytes and assigns the returned bytes through all the
/// iterators in the range [first,last). generate_random_n does the same through all the
/// iterators in the range [first,first + n) if n is positive, otherwise it does nothing.

/// _Requires_: The iterator must belong to a container of unsigned char

/// _Returns_: generate_random_n returns `first + n`
template<typename OutputIterator, typename Size>
OutputIterator generate_random_n(OutputIterator first, Size n)
{
  typedef typename std::iterator_traits<OutputIterator>::value_type input_type;
  static_assert(std::is_same<unsigned char, input_type>::value, "value type needs to be unsigned char");

  if (n > 0)
  {
    std::vector<unsigned char> bytes(n);
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

That should do for the randomness we typically need in a general application. Here's a small test to
illustrate the usage.

```` cpp
void test_random_generator()
{
  using ajd::crypto::random_ok;
  using ajd::crypto::generate_random;
  using ajd::crypto::generate_random_n;

  // see if we have enough randomness.
  assert(random_ok() == true);

  // generate an AES-128 key.
  unsigned char key[16];
  generate_random_n(key, 16);

  // generate a random 64 bit nonce.
  std::vector<unsigned char> nonce(8);
  generate_random(nonce.begin(), nonce.end());

  std::cout << "random passed" << std::endl;
}
````

### Symmetric Key Encryption & Decryption 

There are various for symmetric key encryption that can operate in various modes. This variety adds
up to bunch of options that the programmer has to choose from. One of the goals of the wrapper we're
writing is to hide these choices from the end user. Instead, the wrapper is expected to use a
combination that works well for most case and present a more convenient interface. With that in
mind, the cipher of choice for the wrapper is CTR-AES-128.







[rand]:http://www.openssl.org/docs/crypto/rand.html
[openssl]: http://www.openssl.org/docs/crypto/crypto.html
[bytes]: http://www.openssl.org/docs/crypto/RAND_bytes.html
[final]: https://github.com/aldrin/home/blob/master/web/code/c%2B%2B/crypto/crypto.h
