/// Copyright (c) 2013 Aldrin's Notebook (http://a1dr.in). All rights reserved.
/// You may use any of the code here as long as you retain this copyright notice.

#pragma once

#include <stdexcept>

#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>

#include <boost/array.hpp>
#include <boost/utility.hpp>
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

    /// Check return values from the OpenSSL APIs (private method)
    void checked_(const char *what, bool success)
    {
      if (!success)
      {
        std::string message(what);
        message += " failed";
        throw std::runtime_error(message);
      }
    }

    /// Fills the data buffer with len random bytes. Typically, this overload should not be used and
    /// the variant which takes high leven containers must be preferred.
    void fill_random(unsigned char *data, std::size_t len)
    {
      checked_("random byte generation",
               RAND_bytes(data, len));
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
      checked_("password based key derivation",
               PKCS5_PBKDF2_HMAC(
                 buffer_cast<const char *>(p), buffer_size(p),
                 buffer_cast<const unsigned char *>(s), buffer_size(s),
                 iterations, EVP_sha256(),
                 buffer_size(k), buffer_cast<unsigned char *>(k)));
    }

    /// Generates a keyed or a plain cryptographic hash.
    class hash: boost::noncopyable
    {
    public:
      /// A shorthand typedef for hash value (we're using SHA-256)
      typedef boost::array<unsigned char, 32> value;

      /// The plain hash constructor. Initializes the underlying hash context.
      hash(): keyed_(false), digest_(EVP_sha256()), md_context_(EVP_MD_CTX_create())
      {
        checked_("digest initialization",
                 EVP_DigestInit_ex(md_context_, digest_, NULL));
      }

      /// The keyed hash constructor. Initializes the underlying hash context. The key parameter can
      /// be any contiguous container convertible to a boost::asio::const_buffer using
      /// boost::asio::buffer.
      template<typename C>
      hash(const C &key): keyed_(true), digest_(EVP_sha256())
      {
        HMAC_CTX_init(&hmac_context_);
        const_buffer k(buffer(key));
        checked_("mac initialization",
                 HMAC_Init_ex(&hmac_context_, buffer_cast<const void *>(k), buffer_size(k),
                              digest_, NULL));
      }

      /// Add the contents of the passed container to the underlying context. This method can be
      /// invoked multiple times to add data that needs to be digested. The data parameter can be
      /// any contiguous storage container that can be converted to the boost::asio::const_buffer
      /// using boost::asio::buffer.
      template <typename C>
      hash &update(const C &data)
      {
        const_buffer d(buffer(data));
        checked_("add data to hash",
                 (keyed_ ?
                  HMAC_Update(&hmac_context_, buffer_cast<const unsigned char *>(d), buffer_size(d))
                  : EVP_DigestUpdate(md_context_, buffer_cast<const void *>(d), buffer_size(d))));
        return *this;
      }

      /// Get the resultant hash value. Returns a crypto::hash::value structure that contains the 32
      /// byte SHA256 hash value of the data added to the digest. This method also reinitializes the
      /// underlying context, so the instance can be reused to compute more hashes.
      value finalize()
      {
        value h;
        checked_("finalization of hash",
                 (keyed_ ?
                  HMAC_Final(&hmac_context_, h.data(), 0) :
                  EVP_DigestFinal_ex(md_context_, h.data(), NULL)));
        checked_("reinitialization of hash",
                 (keyed_ ?
                  HMAC_Init_ex(&hmac_context_, NULL, 0, NULL, NULL) :
                  EVP_DigestInit_ex(md_context_, digest_, NULL)));
        return h;
      }

      /// Cleans up the underlying context.
      ~hash()
      {
        keyed_ ? HMAC_CTX_cleanup(&hmac_context_) : EVP_MD_CTX_destroy(md_context_);
      }
    private:
      bool keyed_;
      const EVP_MD *digest_;
      HMAC_CTX hmac_context_;
      EVP_MD_CTX *md_context_;
    };
  }
}
