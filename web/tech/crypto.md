Date: 03/01/2013
Tags: Security, C++
slug: crypto-primitives
Title: Cryptographic Primitives in C++

This page walks through the implementation of an easy-to-use C++ wrapper over the OpenSSL crypto
library. The idea is to go through the OpenSSL documentation once, make the right choices from a
cryptographic point of view, and then, hide all the complexity behind a resuable header. I typically
need the following primitives in the applications I write:

- Random Number Generation 
- Symmetric Key Generation (password-based)
- Message Digests and Message Authentication Codes
- Symmetric Key Encryption & Authenticated Encryption

The wrapper is implemented as a single header file that can be included wherever these primitives
are needed. It includes OpenSSL and Boost headers and links with the OpenSSL crypto library. Take a
look at the CMakelists.txt if you need help on building.

#### Data Buffers

Cryptographic routines work with blocks of data. We'd prefer passing these as high level C++
containers or iterator but the OpenSSL routines require C style raw arrays. Internally, the wrapper
uses `boost::asio::buffer` to bridge this gap of abstractions. The user code can choose any C++
container that guarantees contiguous storage (`std::vector`, `std::string`, raw array) and it would
be converted to a `boost::asio::const_buffer` or `boost::asio::mutable_buffer` as need be. When used
as output parameters, it is the responsibility of the user code to ensure that the passed container
has enough room to receive the generated data.
        
#### Secure Random Number Generation

OpenSSL provides an interface around the PRNG provided by the underlying operating system. It also
provides a way to check if the PRNG has been initialized properly, or if it is needs additional seed
data. The default initialization is usually sufficient so the wrapper provides just two method
related to random number generation.

``` c++
namespace ajd { namespace crypto {
    /// Checks if the underlying PRNG is sufficiently seeded. In the (exceptional) situation where
    /// this check returns 'false', you must use the OpenSSL seeding routines RAND_seed, RAND_add
    /// directly to add entropy to the underlying PRNG.
    bool prng_ok() { return RAND_status() == 1; }

    /// Fills the passed container with random bytes. The method works with any container that can
    /// be converted to a boost::asio::mutable_buffer using the boost::asio::buffer helper.
    template<typename C> void fill_random(C &c)
```

The following code demonstrates how these routines can be used to fill containers with random bytes.

``` c++
void random_generation()
{
  using namespace ajd;
  assert(crypto::prng_ok());    // check PRNG state
  unsigned char arr[16];
  crypto::fill_random(arr);     // fill a raw array
  std::vector<unsigned char> vec(16);
  crypto::fill_random(vec);     // fill a std::vector
  boost::array<unsigned char, 16> barr;
  crypto::fill_random(barr);    // fill a boost::array or std::array
}
``` 

An alternative implementation would be to only provide a random byte generator that can be plugged
into the STL `generate` algorithm and use it to fill arbitrary containers. However, since OpenSSL's
RAND_bytes does not work with arbitrary iterators, that'd have required us to first generate bytes
and then copy them. TODO

#### Password Based Symmetric Key Generation

OpenSSL provides implementation of many ciphers. One of the goals of the wrapper is to make the most
suitable cryptographic choices and free the user from having to make any. With that in mind, the
only cipher we deal with is AES-128, and that fixes up the size of the key to 128 bits and lets us
define a few convenience typedefs to make thing easier:

``` c++
typedef boost::array<unsigned char, 16> symmetric_key; // shorthand for AES-128 key
```

The typedef is just a syntactic shorthand and we still need a way to populate a `symmetric_key`
structure with the right bits. One way is to fill it with random bytes using the `fill_random`
routine but more commonly we'd want to derive the key bits from a user provided password. The
standard way to do this is using the PBKDF2 algorithm defined in PKCS#5. The algorithm requires a
hash function which it invokes a fixed number of times to derive the key bits. OpenSSL provides an
implementation of the algorithm that wrapper invokes with the hash function set to SHA256 and the
iteration count set to 10000. Here's the function signature:

``` c++
/// Derives a key from a password using PBKDF2. The hash function is fixed to SHA256 and the
/// default iteration count is 10000. The password and salt parameters can be any contiguous
/// container convertible to a boost::asio::const_buffer using boost::asio::buffer. The key
/// parameter must be convertible to boost::asio::mutable_buffer (use symmetric_key).
template <typename C1, typename C2, typename C3>
void derive_key(C3 &key, const C1 &passwd, const C2 &salt, int iterations = 10000)
```

Recall that the salt here can be any public value that will be persisted between application
runs. Repeated runs of this key derivation with the same password and salt value produce the same
key bits and that means we don't need to persist the actual key bits and deal with the complexity of
secure storage of secret keys. However, this also assumes that the application can interact with the
end user and prompt for the password. That assumption is not valid for some applications that
require non-interactive startup (ex: services, daemons)

Here's a sample invocation of the key derivation routine:

``` c++
void key_generation()
{
  using namespace ajd;
  crypto::symmetric_key key;
  boost::array<unsigned char, 16> salt;
  crypto::fill_random(salt);  // random salt.
  crypto::derive_key(key, std::string("password"), salt); // password derived key.
}
```

#### Message Digests and Message Authentication Codes

Cryptographic hashes are used as compression functions that _digest_ an arbitrary sized message into
a small fingerprint that uniquely represents it. Although their primary use is to serve as a
building block for implementing integrity checks a hash, by itself, cannot guarantee integrity. An
adversary capable of modifying the message is also capable of recomputing the hash of the modified
message to send along. We need to combine plain hashes with other primitives like digital signatures
to guarantee integrity with authenticity. The symmetric-key equivalent of a digital signature is a
message authentication code (MAC). A MAC is a keyed-hash, i.e. a cryptographic hash that can only be
generated by those who posses an assumed shared key. The assumption of secrecy of the key limits the
possible origins and thus provides us the guarantee that an adversary couldn't have generated it.

The wrapper can generate both plain and keyed hashes by wrapping SHA-256 and HMAC-SHA-256
respectively. The user code needs to use the following class:

``` c++
/// Generates a keyed or a plain cryptographic hash.
class hash: boost::noncopyable
{
public:
  /// The plain hash constructor. Initializes the underlying hash context.
  hash();

  /// The keyed hash constructor. Initializes the underlying hash context. The key parameter can
  /// be any contiguous container convertible to a boost::asio::const_buffer using
  /// boost::asio::buffer.
  template<typename C> hash(const C &key);

  /// Add the contents of the passed container to the underlying context. This method can be
  /// invoked multiple times to add data that needs to be digested. The data parameter can be
  /// any contiguous storage container that can be converted to the boost::asio::const_buffer
  /// using boost::asio::buffer.
  template <typename C> hash &update(const C &data);

  /// A shorthand typedef for hash value (we're using SHA-256)
  typedef boost::array<unsigned char, 32> value;

  /// Get the resultant hash value. Returns a crypto::hash::value structure that contains the 32
  /// byte SHA256 hash value of the data added to the digest. This method also reinitializes the
  /// underlying context, so the instance can be reused to compute more hashes.
  value finalize();

  /// ... details ...
};
``` 

Note that there are two constructors one for keyed and other for plain hashes. User code can use
this class as shown in the sample below:

```c++
void message_digest()
{
  using namespace ajd;
  crypto::hash md;                        // the hash object
  md.update("hello");                     // add data
  md.update("world");                     // more data
  crypto::hash::value sha(md.finalize()); // get the hash
}

void message_authentication_code()
{
  using namespace ajd;
  crypto::symmetric_key key;               // the hash key
  crypto::derive_key(key, "pass", "salt"); // password derived key.
  crypto::hash h(key);                     // the keyed-hash object
  h.update("hello").update("world");       // add data
  crypto::hash::value mac(h.finalize());   // get the mac
}
```

#### Symmetric Key Encryption

Encryption is the usually the goal of using crypto primitives. As discussed we have chosen AES-128
as our cipher, so all encryption we need uses it as our
