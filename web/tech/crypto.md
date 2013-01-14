Date: 14/01/2013
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of an easy-to-use C++ wrapper over the OpenSSL
[crypto library][crypto]. The idea is to go through the OpenSSL documentation once, make the right
choices from a cryptographic point of view, and then, hide all the complexity behind a reusable
header. The following primitives are typically used in the applications I write:

- Random Number Generation
- Password Based Symmetric Key Generation (using PBKDF2 with HMAC-SHA-256)
- Message Digests and Authentication Codes (using SHA-256 and HMAC-SHA-256)
- Authenticated Symmetric Key Encryption (using AES-128-GCM)

The wrapper is a [single header file][header] that can be included wherever these primitives are
needed. It includes OpenSSL and Boost headers and executables using it will need to have the OpenSSL
libraries on their link line. Here is some [sample code][app] code and here are the [tests][vectors]
to validate the implementation against the available test vectors.

#### Data Buffers

First things first, cryptographic routines work with blocks of data and we need a way to pass these
in and out of the wrapper routines. We'd prefer passing data these as high level C++ containers or
iterators ranges but OpenSSL routines work with C-style raw buffers. To bridge this gap in
abstractions, the wrapper makes use of the [`boost::asio::buffer`][buffer] function. This function
takes in any C++ contiguous storage container and extracts a raw pointer and length pair capable of
being to OpenSSL routines. What this means is that you can pass a `std::vector`, `std::string`,
`std::array`, `boost::array`, a POD array, or even a string literal to any of the routines that
expect a data buffer. Furthermore, most of the blocks we deal with are 128 bits (16 byte) long, so
the wrapper defines a convenience typedef as a shorthand:

``` c++
namespace ajd { namespace crypto {
    /// A convenience typedef for a 128 bit block.
    typedef boost::array<unsigned char, 16> block;
```

Note that all wrapper definitions are inside the `ajd::crypto` namespace. All executable code is
assumed to be prefixed by a `using namespace ajd;`.

#### Secure Random Number Generation

OpenSSL provides an interface around the PRNG provided by the underlying operating system. It also
provides a way to check if the PRNG has been initialized properly or if it needs additional seed
data. The default initialization is usually sufficient so the wrapper provides just two methods
related to random number generation.

``` c++
/// Checks if the underlying PRNG is sufficiently seeded. In the (exceptional) situation where
/// this check returns 'false', you /must/ use the OpenSSL seed routines RAND_seed, RAND_add
/// directly to add entropy to the underlying PRNG.
bool prng_ok() { return RAND_status() == 1; }

/// Fills the passed container with random bytes.
template<typename C> void fill_random(C &c)
```

The following code demonstrates how these routines can be used to fill containers with random
bytes. 

``` c++
void random_generation()
{
  assert(crypto::prng_ok());          // check PRNG state

  crypto::block buffer;               // use the convenience typedef
  crypto::fill_random(buffer);        // fill it with random bytes.
  unsigned char arr[1024];            // use a static POD array
  crypto::fill_random(arr);           // fill it with random bytes
  std::vector<unsigned char> vec(16); // use a std::vector
  crypto::fill_random(vec);           // fill it with random bytes
}
``` 

The code above also serves as an example of how C++ containers can be passed into the wrapper
routines. Throughout the wrapper, a templated argument (like `C &c` here) can accept any continuous
C++ container value (more precisely, any container that can be converted to a
`boost::asio::const_buffer` or a `boost::asio::mutable_buffer` using the `boost::asio::buffer`
function.)

#### Password Based Symmetric Key Generation

Symmetric ciphers require secure keys and one way to generate them is using the `fill_random`
routine we saw above. More commonly, however, we'd want to derive the key bits from a user provided
password. The standard way to do this is using the [PBKDF2][pbkdf] algorithm which iterates a pseudo
random function with the passed password and salt a fixed number of times to derive the key
bits. The wrapper invokes OpenSSL's implementation of the algorithm with HMAC-SHA-256 as the chosen
pseudo random function. Here's the function signature:

``` c++
/// Derives a  key from a  password and salt  using PBKDF2 with  HMAC-SHA256 as the  chosen PRF.
/// Although the routine can generate arbitrary length  keys, it is best to use crypto::block as
/// the type for the key  parameter, since it fixes the key length to 128  bit which is what the
/// other primitives in the wrapper (crypto::hash, crypto::cipher) require.
/// @param key      (output) container populated with the key bits
/// @param password (input)  container holding the user password
/// @param salt     (input)  container holding the salt bytes
/// @param c        (input)  PBKDF2 iteration count (default=10000)
template <typename C1, typename C2, typename C3>
void derive_key(C3 &key, const C1 &passwd, const C2 &salt, int c = 10000)
```

Recall that the salt here can be any public value that will be persisted between application
runs. Repeated runs of this key derivation with the same password and salt value produce the same
key bits and that means we don't need to persist the actual key bits and deal with the complexity of
secure storage of secret keys. However, this also assumes that the application can interact with the
end user and prompt for the password. That assumption is not valid for some applications that
require non-interactive start-up (ex: services, daemons)

Here's a sample invocation of the key derivation routine:

``` c++
void key_generation()
{
  crypto::block key;                         // 128 bit key
  crypto::block salt;                        // 128 bit salt
  crypto::fill_random(salt);                 // random salt.
  crypto::derive_key(key, "password", salt); // password derived key.
}
```

#### Message Digests and Message Authentication Codes

Cryptographic hashes are used as compression functions that _digest_ an arbitrary sized message into
a small fingerprint that uniquely represents it. Although their primary use is to serve as a
building block for implementing integrity checks, a hash, by itself, cannot guarantee integrity. An
adversary capable of modifying the message is also capable of recomputing the hash of the modified
message to send along. For authenticity we need to use a message authentication code (MAC). A MAC is
a keyed-hash, i.e. a hash that can only be generated by those who posses an assumed shared key. The
assumption of secrecy of the key limits the possible origins and thus provides us the guarantee that
an adversary couldn't have generated it.

The wrapper uses [SHA-256][sha] for generating plain digests and [HMAC][hmac] with SHA-256 for
MACs. These details, however, are hidden behind the following class:

``` c++
/// Generates a keyed or a plain cryptographic hash.
class hash: boost::noncopyable
{
public:
  /// A convenience typedef for a 256 SHA-256 value.
  typedef boost::array<unsigned char, 32> value;

  /// The plain hash constructor. Initializes the underlying hash context.
  hash();

  /// The keyed hash constructor. Initializes the underlying hash context.
  /// @param key (input) container holding the secret key
  template<typename C> hash(const C &key);

  /// Add the  contents of the passed  container to the  underlying context. This method  can be
  /// invoked multiple times to add all the data that needs to be hashed.
  /// @param data (input) container holding the input data
  template <typename C> hash &update(const C &data);

  /// Get the  resultant hash value. This  method also reinitializes the  underlying context, so
  /// the same instance can be reused to compute more hashes.
  /// @param sha (output) container populated with the hash/mac bits
  template<typename C> void finalize(C &sha);

  /// ... details ...
};
``` 

The following code shows how the class can be used:

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
}
```

#### Authenticated Symmetric Key Encryption

Encryption is the usually the end goal of using cryptographic primitives. In the past, I've used
plain encryption (AES-128 in CBC or CTR mode) for providing confidentiality of data. Lately, I
learned that though plain encryption is sufficient for confidentiality, it does not guard against
tampering of encrypted data. These schemes can not detect modifications in ciphertext and decrypt
the tweaked data as they would decrypt any other ciphertext. A smart adversary can make use of this
fact to make calibrated modifications to the ciphertext and end up with the desired plaintext in
the decrypted data.

To recommended way to guard against these attacks is to use the cipher in an authenticated
encryption mode like the [Galois Counter Mode][gcm] (GCM). The wrapper provides the following class
to deal with it:

``` c++
/// Provides authenticated encryption (AES-128-GCM)
class cipher : boost::noncopyable
{
public:
  /// Encryption mode  constructor, only takes key  and IV parameters.  Initializes the instance
  /// for encryption. The  key should be 128  bit (since we're with AES-128).  Typically, the IV
  /// should be 128 bit IV too but GCM supports  other IV sizes, so those can be passed to.
  /// @param key (input) container holding 128 key bits (use crypto::block)
  /// @param iv  (input) container holding 128 initialization vector bits (use crypto::block)
  template<typename K, typename I> cipher(const K &key, const I &iv);

  /// Decryption  mode constructor,  takes key,  IV and  the authentication  tag  as parameters.
  /// Initializes  the cipher  for  decryption and  sets  the passed  tag  up for  authenticated
  /// decryption. The key  and IV should be the  same that were used to  generate the ciphertext
  /// you're trying to decrypt (obviously). The seal parameter should contain the authentication
  /// tag returned by the 'seal' call after encryption.
  /// @param key  (input) container holding 128 key bits (use crypto::block)
  /// @param iv   (input) container holding 128 initialization vector bits (use crypto::block)
  /// The seal parameter does not have a 'const' with it because of the OpenSSL API.
  /// @param seal (input) container holding 128 authentication tag bits (use crypto::block)
  template<typename K, typename I, typename S> cipher(const K &key, const I &iv, S &seal);

  /// The  cipher transformation  routine. This  encrypts or  decrypts the  bytes from  the 'in'
  /// buffer and places them into the 'out'  buffer.  Since GCM does not require any padding the
  /// output buffer size  should be the same  as the input.  If you  have unencrypted associated
  /// data that must be added using 'associate_data' first.
  /// @param input  (input)  plaintext or ciphertext (for encryption or decryption resp.)
  /// @param output (output) inverse of the input
  template<typename I, typename O> cipher &transform(const I &input, O &output);

  /// Adds associated authenticated data, i.e. data which is accounted for in the authentication
  /// tag, but  is not encrypted.  Typically, this  is used for  associated meta data  (like the
  /// packet header in a network protocol). This data must be added /before/ any message text is
  /// added to the cipher.
  /// @param aad (input) container with associated data
  template<typename A> cipher &associate_data(const A &aad);

  /// The encryption finalization routine. Populates  the authentication tag "seal" that must be
  /// passed  along for  successful decryption.   Any modifications  in the  cipher text  or the
  /// associated data will be detected by the decryptor using this seal.
  /// @param seal (output) container to be populated with the tag bits
  template<typename S> void seal(S &seal);

  /// The  decryption  finalization  routine. Uses  the  authentication  tag  to verify  if  the
  /// decryption was successful. If the tag verification fails an exception is thrown, if all is
  /// well,  the method silently  returns.  If  an exception  is thrown,  the decrypted  data is
  /// corrupted and /must/ not be used.
  void verify();

  /// ... details ...
};
```

Authenticated encryption schemes produce an authentication tag (called _seal_ here) along with the
ciphertext. The tag needs to be presented during decryption and helps detect modifications to the
ciphertext. The `crypto::cipher::seal` and `crypto::cipher::verify` method wrap this
behavior. During encryption, after all the plaintext has been transformed to ciphertext the user
code must invoke the `seal` operation to get the authentication tag. The decryption mode constructor
requires this tag and after all the ciphertext has been transformed to plaintext the user code must
invoke the `verify` method to check if the tag verifies properly. If `verify` throws an exception
the decrypted plaintext is compromised and must not be used.

Another feature of authenticated encryption schemes is that they allow addition of _authenticated
associated data_. This data is not encrypted but is accounted for in the authentication tag,
i.e. adversarial modifications to this unencrypted data will also be detected by the `verify`
call. OpenSSL implementation requires that all associated data must be added _before_ the plaintext
is added.

The following sample shows how the class can be used:

``` c++
void encryption()
{
  crypto::block iv;                                                // initialization vector
  crypto::block key;                                               // encryption key
  crypto::block seal;                                              // container for the seal
  crypto::fill_random(iv);                                         // random initialization vector
  crypto::fill_random(key);                                        // random key will do (for now)
  unsigned char date[] = {14, 1, 13};                              // associated data
  std::string text("can you keep a secret?");                      // message (plain-text)
  std::vector<unsigned char> ciphertext(text.size());              // container for encrypted data
  {
    crypto::cipher cipher(key, iv);                                // initialize cipher (encrypt mode)
    cipher.associate_data(date);                                   // add associated data first
    cipher.transform(text, ciphertext);                            // do transform (i.e. encrypt)
    cipher.seal(seal);                                             // get the encryption seal
  }
  std::vector<unsigned char> decrypted(ciphertext.size());         // container for decrypted data
  {
    crypto::cipher cipher(key, iv, seal);                          // initialize cipher (decrypt mode)
    cipher.associate_data(date);                                   // add associated data first
    cipher.transform(ciphertext, decrypted);                       // do transform (i.e. decrypt)
    cipher.verify();                                               // check the seal
  }
  assert(std::equal(text.begin(), text.end(), decrypted.begin())); // sanity (decrypted == plaintext)
}
```

Modification to the ciphertext or the associated data will cause `crypto::cipher::verify` to throw
an exception, as shown in the following snippet:

``` c++
  date[0] = 15;                                                    // modify the associated data
  {
    crypto::cipher cipher(key, iv, seal);                          // initialize cipher (decrypt mode)
    cipher.associate_data(date);                                   // add associated data first
    cipher.transform(ciphertext, decrypted);                       // try decryption again
    try
    {
      cipher.verify();                                             // should throw an exception
      assert(false);                                               // should never be reached
    }
    catch (...) {}
  }

  date[0] = 14;                                                    // revert associated data
  ciphertext[0] = '\0';                                            // modify ciphertext.
  {
    crypto::cipher cipher(key, iv, seal);                          // initialize cipher (decrypt mode)
    cipher.associate_data(date);                                   // add associated data first
    cipher.transform(ciphertext, decrypted);                       // try decryption again
    try
    {
      cipher.verify();                                             // should throw an exception
      assert(false);                                               // should never be reached
    }
    catch (...) {}
  }
```

That completes the list of primitives we started off with. There's more to be done, specifically for
public key cryptography, but that is for some other day.

[crypto]: http://www.openssl.org/docs/crypto/crypto.html 
[header]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/crypto.h
[buffer]: http://www.boost.org/doc/libs/release/doc/html/boost_asio/reference/buffer.html
[pbkdf]: http://tools.ietf.org/html/rfc2898
[hmac]: http://tools.ietf.org/html/rfc2104
[sha]: http://csrc.nist.gov/groups/ST/toolkit/secure_hashing.html
[gcm]: http://csrc.nist.gov/publications/nistpubs/800-38D/SP-800-38D.pdf
[app]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/crypto.cpp
[vectors]: https://github.com/aldrin/home/blob/master/code/c%2B%2B/crypto/vectors.cpp
