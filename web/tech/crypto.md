Date: 14/01/2013
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of an easy-to-use C++ wrapper over the OpenSSL
[crypto library][crypto]. The idea is to go through the OpenSSL documentation once, make the right
choices from a cryptographic point of view, and then, hide all the complexity behind a reusable
header. The following primitives are typically used in the applications I write:

- Random Number Generation
- Password Based Symmetric Key Generation (PBKDF2/HMAC-SHA-256)
- Message Digests and Authentication Codes (SHA-256 & HMAC-SHA-256)
- Authenticated Encryption with Associated Data (AES-128-GCM)

The wrapper is a [single header file][header] that can be included wherever these primitives are
needed. It includes OpenSSL and Boost headers and will require linking with the OpenSSL object
libraries. Here is a [sample][app] and here are the [tests][vectors]. 

#### Data Buffers

Most of the wrapper functions work on blocks of data and we need a way to pass these in and out of
the wrapper routines. Any C++ container that guarantees contiguous storage (i.e. `std::vector`,
`std::string`, `std::array`, `boost::array` or a raw char array) can be passed as the argument to
any wrapper function that takes a data buffer as a parameter.

Having said that, it is best to avoid using dynamic STL containers for storing sensitive data
because it is diffcult to scrub them off once we're done using the secrets. The implementations of
these containers are allowed to reallocate and copy their contents in the memory and may end up with
inaccessible copies of sensitive data that we can't overwrite. Simpler containers like
`boost::array` or raw char arrays are better for this purpose. You can also use the following typedef:

``` c++
namespace ajd { namespace crypto {
    /// A convenience typedef for a 128 bit block.
    typedef boost::array<unsigned char, 16> block;
    /// Remove sensitive data from the buffer
    template<typename C> void cleanse(C &c)
```

The wrapper also provides a `cleanse` method that can be used to overwrite secret data in the
buffers. This method does not deallocate any memory, it only overwrites the contents of the passed
buffer by invoking `OPENSSL_cleanse` on it.

#### Secure Random Number Generation

OpenSSL provides a simple interface around the underlying operating system PRNG. This is exposed by
the wrapper using the following two functions:

``` c++
/// Checks if the PRNG is sufficiently seeded
bool prng_ok();
/// Fills the passed container with random bytes.
template<typename C> void fill_random(C &c);
```

`prng_ok` checks if the PRNG has been seeded sufficiently and `fill_random` routine fills any
mutable container with random bytes. In the exceptional situation that `prng_ok` returns false you
_must_ use use the OpenSSL seed routines `RAND_seed` and `RAND_add` directly to add entropy to the
underlying PRNG.

Here's how you can use them:

``` c++
void random_generation()
{
  assert(crypto::prng_ok());          // check PRNG state

  crypto::block buffer;               // use the convenience typedef
  crypto::fill_random(buffer);        // fill it with random bytes
  unsigned char arr[1024];            // use a static POD array
  crypto::fill_random(arr);           // fill it with random bytes
  std::vector<unsigned char> vec(16); // use a std::vector
  crypto::fill_random(vec);           // fill it with random bytes
}
``` 


#### Password Based Symmetric Key Generation

Symmetric ciphers require secure keys and one way to generate them is using the `fill_random`
routine seen above. More commonly however, we'd want to derive the key bits from a user provided
password. The standard way to do this is using the [PBKDF2][pbkdf] algorithm which derives the key
bits by iterating over a pseudo random function with the password and a salt as inputs. The wrapper
sets HMAC-SHA-256 as the chosen pseudo random function and uses a default iteration count of 10000.

``` c++
/// Derive a key using PBKDF2-HMAC-SHA-256
template <typename C1, typename C2, typename C3>
void derive_key(C3 &key, const C1 &passwd, const C2 &salt, int c = 10000)
```

The salt can be any public value that will be persisted between application runs. Repeated
invocations of this key derivation routine with the same password and salt value produce the same
key bits. This saves us from the hassle of securely storing the secret key assuming that the
application can interact with a human user and prompt for the password.

Here's a sample invocation of the key derivation routine:

``` c++
void key_generation()
{
  crypto::block key;                         // 128 bit key
  crypto::block salt;                        // 128 bit salt
  crypto::fill_random(salt);                 // random salt
  crypto::derive_key(key, "password", salt); // password derived key
  crypto::cleanse(key)                       // clear sensitive data
}
```

#### Message Digests and Message Authentication Codes

Cryptographic hashes are compression functions that _digest_ an arbitrary sized message into a small
fingerprint that uniquely represents it. Although they are the building blocks for implementing
integrity checks, a hash, by itself, cannot guarantee integrity. An adversary capable of modifying
the message is also capable of recomputing the hash of the modified message to send along. For an
additional guarantee on the origin we need a stronger primitive which is the message authentication
code (MAC). A MAC is a keyed-hash, i.e. a hash that can only be generated by those who posses an
assumed shared key. The assumption of secrecy of the key limits the possible origins and thus
provides us the guarantee that an adversary couldn't have generated it.

MD5 should not be used and SHA-1 hashes are considered weak and unsuitable for all new
applications. The wrapper uses [SHA-256][sha] for generating plain digests and [HMAC][hmac] with
SHA-256 for MACs.

``` c++
/// Generates a keyed or a plain cryptographic hash.
class hash: boost::noncopyable
{
public:
  /// A convenience typedef for a 256 SHA-256 value.
  typedef boost::array<unsigned char, 32> value;
  /// The plain hash constructor (for message digests).
  hash();
  /// The keyed hash constructor (for MACs) 
  template<typename C> hash(const C &key);
  /// Include the contents of the passed container for hashing.
  template <typename C> hash &update(const C &data);
  /// Get the resultant hash value.
  template<typename C> void finalize(C &sha);

  /// ... details ...
};
``` 

The default constructor of the class initializes the instance for message digests. The other
constructor takes a key as input and initializes the instance for message authentication codes. Once
initialized, the data to be hashed can be added by invoking the `update` method (multiple times, if
required). The resulting hash or MAC is a SHA-256 hash (a 256 bit value) that can be extracted using
the `finalize` method. The shorthand typedef `hash::value` can be used to hold the result. The
`finalize` method also reinitializes the underlying hash context and resets the instance for a fresh
hash computation.

Here's how you can use the class:

```c++
void message_digest()
{
  crypto::hash md;              // the hash object
  crypto::hash::value sha;      // the hash value
  md.update("hello world!");    // add data
  md.update("see you world!");  // add more data
  md.finalize(sha);             // get digest value
}

void message_authentication_code()
{
  crypto::block key;            // the hash key
  crypto::fill_random(key);     // random key will do (for now)
  crypto::hash h(key);          // the keyed-hash object
  crypto::hash::value mac;      // the mac value
  h.update("hello world!");     // add data
  h.update("see you world!");   // more data
  h.finalize(mac);              // get the MAC code
  crypto::cleanse(key)          // clean senstive data
}
```

#### Authenticated Encryption with Associated Data

Encryption guarantees confidentiality and [authenticated encryption][aenc] extends that guarantee to guard
against tampering of encrypted data. Operation modes like CBC or CTR cannot detect modifications to
the ciphertext and decrypt tweaked data as they would decrypt any other ciphertext. An adversary can
use this fact to make calibrated modifications to the ciphertext and end up with the desired
plaintext in the decrypted data. The recommended way to guard against such attacks is to use an
authenticated encryption mode like the [Galois Counter Mode][gcm] (GCM).

Authenticated encryption schemes differ from the simpler schemes in that they produce an extra
output along with the cipher text. This extra output is an authentication tag that is required as an
input at the time of decryption where it is used to detect modifications in the ciphertext.

Another feature of authenticated encryption is their support for associated data. Network protocol
messages include data (ex: header fields in packets) that doesn't need to be encrypted but must be
guarded against modifications in transit. Authenticated encryption schemes allow the addition of
such data into the tag computation. So while the adversary can view this data in transit, it cannot
be modified without the decryption routine noticing it.

The following class provides authenticated encryption with associated data:

``` c++
/// Provides authenticated encryption (AES-128-GCM)
class cipher : boost::noncopyable
{
public:
  /// Encryption mode constructor.
  template<typename K, typename I>
  cipher(const K &key, const I &iv);
  /// Decryption mode constructor.
  template<typename K, typename I, typename S>
  cipher(const K &key, const I &iv, S &seal);
  /// The cipher transformation.
  template<typename I, typename O>
  cipher &transform(const I &input, O &output);
  /// Adds associated authenticated data.
  template<typename A> cipher &associate_data(const A &aad);
  /// The encryption finalization routine.
  template<typename S> void seal(S &seal);
  /// The decryption finalization routine (throws if the ciphertext is corrupt)
  void verify();

  /// ... details ...
};
```


The `crypto::cipher` class has two constructors. The 2 argument variant takes a key and an
initialization vector (128 bits each) and initializes the instance for encryption. Plaintext can be
transformed into ciphertext using the `transform` method. The GCM mode does not use any padding so
the output ciphertext buffer must be as big as the input plaintext buffer. If there's any associated
data that needs to be sent along with the ciphertext it can be added using the `associate_data`
method. Note that the OpenSSL implementation of GCM requires that associated data is added _before_
the plaintext is added (i.e. all calls to `associate_data` must precede all calls to `transform`.)
Once all the data has been added, the `seal` method must be invoked to obtain the authentication tag
(128 bits) and it must be sent along with the ciphertext.

The 3 argument constructor takes a key, an IV and the encryption seal as inputs and initializes the
instance for decryption. Ciphertext can then be transformed to plaintext using the `transform`
method (after adding any associated data using the `associate_data` method). Before using the
plaintext, the `verify` method must be invoked to detect any tampering in the ciphertext or
associated data. If all is well the method silently returns, however if the seal does not match the
expected tag value, an exception is raised and the decrypted plaintext _must_ be rejected.

The following sample shows the usage:

``` c++
void authenticated_encrypt_decrypt()
{
  crypto::block iv;                           // initialization vector
  crypto::block key;                          // encryption key
  crypto::block seal;                         // container for the seal
  crypto::fill_random(iv);                    // random initialization vector
  crypto::fill_random(key);                   // random key will do (for now)
  unsigned char date[] = {14, 1, 13};         // associated data
  std::string text("can you keep a secret?"); // message (plain-text)

  std::vector<unsigned char> ciphertext(text.size());
  {
    crypto::cipher cipher(key, iv);           // initialize cipher (encrypt mode)
    cipher.associate_data(date);              // add associated data first
    cipher.transform(text, ciphertext);       // do transform (i.e. encrypt)
    cipher.seal(seal);                        // get the encryption seal
  }

  std::vector<unsigned char> decrypted(ciphertext.size());
  {
    crypto::cipher cipher(key, iv, seal);     // initialize cipher (decrypt mode)
    cipher.associate_data(date);              // add associated data first
    cipher.transform(ciphertext, decrypted);  // do transform (i.e. decrypt)
    cipher.verify();                          // check the seal
  }
  
  crypto::cleanse(key)                        // clear senstive data
```

That completes the list of primitives we started off with. There's more to be done, in particular,
some for primitives that use public key cryptography, but I'll leave that for some other day.

[hmac]: http://tools.ietf.org/html/rfc2104
[pbkdf]: http://tools.ietf.org/html/rfc2898
[crypto]: http://www.openssl.org/docs/crypto/crypto.html 
[sha]: http://csrc.nist.gov/groups/ST/toolkit/secure_hashing.html
[gcm]: http://csrc.nist.gov/publications/nistpubs/800-38D/SP-800-38D.pdf
[aenc]: http://csrc.nist.gov/groups/ST/toolkit/BCM/modes_development.html#01
[app]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/crypto.cpp
[header]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/crypto.h
[vectors]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/vectors.cpp
[buffer]: http://www.boost.org/doc/libs/release/doc/html/boost_asio/reference/buffer.html

