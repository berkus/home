/// Copyright (c) 2013 Aldrin's Notebook (http://a1dr.in). All rights reserved.
/// You may use any of the code here as long as you retain this copyright notice.

#pragma once

#include <stdexcept>

#include <openssl/evp.h>
#include <openssl/rand.h>

#include <boost/array.hpp>
#include <boost/asio/buffer.hpp>

namespace ajd
{
  namespace crypto
  {
    using boost::asio::buffer;
    using boost::asio::buffer_cast;
    using boost::asio::buffer_size;
    using boost::asio::const_buffer;
    using boost::asio::mutable_buffer;
    /// Checks if the underlying PRNG is sufficiently seeded. In the (exceptional) situation where
    /// this check returns 'false', you must use the OpenSSL seed routines RAND_seed, RAND_add
    /// directly to add entropy to the underlying PRNG.
    bool prng_ok() { return RAND_status() == 1; }

    /// Fills the data buffer with len random bytes. Typically, this overload should not be used and
    /// the variant which takes high leven containers must be preferred.
    void fill_random(unsigned char *data, std::size_t len)
    {
      if (!RAND_bytes(data, len))
      {
        throw std::runtime_error("random number generation failed");
      }
    }

    /// Fills the passed container with random bytes. The method works with any container that can
    /// be converted to a boost::asio::mutable_buffer using the boost::asio::buffer helper.
    template<typename C> void fill_random(C &c)
    {
      mutable_buffer b(buffer(c));
      fill_random(buffer_cast<unsigned char *>(b), buffer_size(b));
    }

    /// This typedef is just a shorthand for an AES-128 key
    typedef boost::array<unsigned char, 16> symmetric_key;
    /// This typedef is just a shorthand for an AES-128 IV
    typedef boost::array<unsigned char, 16> initialization_vector;

    /// Derives a key from a password using PBKDF2. The hash function is fixed to SHA256 and the
    /// default iteration count is 10000. The password and salt parameters can be any contiguous
    /// container convertible to a boost::asio::const_buffer using boost::asio::buffer. The key
    /// parameter must be convertible to boost::asio::mutable_buffer (use symmetric_key).
    template <typename C1, typename C2, typename C3>
    void derive_key(C3 &key, const C1 &passwd, const C2 &salt, int iterations = 10000)
    {
      const_buffer s(buffer(salt));
      mutable_buffer k(buffer(key));
      const_buffer p(buffer(passwd));

      if (!PKCS5_PBKDF2_HMAC(
            buffer_cast<const char *>(p), buffer_size(p),
            buffer_cast<const unsigned char *>(s), buffer_size(s),
            iterations, EVP_sha256(),
            buffer_size(k), buffer_cast<unsigned char *>(k)))
      {
        throw std::runtime_error("password based key derivation failed");
      }
    }
  }
}
