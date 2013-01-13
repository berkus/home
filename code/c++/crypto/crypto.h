/// Copyright (c) 2013 Aldrin's Notebook (http://a1dr.in). All rights reserved.
/// You may use any of the code here as long as you retain this copyright notice.

#pragma once

#include <stdexcept>

#include <openssl/err.h>
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
        message += " failed: ";
        message += ERR_error_string(ERR_get_error(), NULL);
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

    /// An AES block, shorthand type for defining key, iv, salt values.
    typedef boost::array<unsigned char, 16> block;

    /// Derives a key from a password using PBKDF2. The hash function is fixed to SHA256 and the
    /// default iteration count is 10000. The password and salt parameters can be any contiguous
    /// container convertible to a boost::asio::const_buffer using boost::asio::buffer. The key
    /// parameter must be convertible to boost::asio::mutable_buffer (use crypto::block).
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
      typedef boost::array<unsigned char, 32> sha256;

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
      sha256 finalize()
      {
        sha256 h;
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

    /// Provides authenticated encryption (AES-128-GCM)
    class cipher : boost::noncopyable
    {
    public:
      /// Encryption mode constructor, only takes key and IV parameters. Initializes the instance
      /// for encryption. The key should be 128 bit (since we're with AES-128). Typically, the IV
      /// should be 128 bit IV too but GCM supports other IV sizes those can be passed to. Both
      /// parameters can be any contiguous storage container that can be converted to the
      /// boost::asio::const_buffer using boost::asio::buffer.
      template<typename K, typename I>
      cipher(const K &key, const I &iv): encrypt_(true)
      {
        initialize(buffer(key), buffer(iv));
      }

      /// Decryption mode constructor, takes key, IV and the authentication tag as
      /// parameters. Initializes the cipher for decryption and sets the passed tag up for
      /// authenticated decryption.

      /// The key and IV should be the same that were used to generate the ciphertext you're trying
      /// to decrypt (obviously). The seal parameter should contain the authentication tag returned
      /// by the 'seal' call after encryption. The key and IV parameters can be any contiguous
      /// storage container that can be converted to the boost::asio::const_buffer using
      /// boost::asio::buffer. The seal parameter needs to be a mutable_buffer because the OpenSSL
      /// API to set the tag requires modifiable buffers.
      template<typename K, typename I, typename S>
      cipher(const K &key, const I &iv, S &seal): encrypt_(false)
      {
        initialize(buffer(key), buffer(iv));
        mutable_buffer s(buffer(seal));
        checked_("set tag",
                 EVP_CIPHER_CTX_ctrl
                 (&context_, EVP_CTRL_GCM_SET_TAG, buffer_size(s), buffer_cast<void *>(s)));
      }

      /// The cipher transformation routine. This encrypts or decrypts the bytes in the in buffer
      /// and places the output into the out buffer. Since GCM does not require any padding the
      /// output buffer size should be the same as the input. Note that if your message contains
      /// unencrypted associated data, that must be added before calling this.

      /// The in and out parameters can be any contiguous storage container that can be converted to
      /// the boost::asio::const_buffer and boost::asio::mutable_buffer using boost::asio::buffer.
      template<typename I, typename O>
      cipher &transform(const I &in, O &out)
      {
        int outl;
        const_buffer i(buffer(in));
        mutable_buffer o(buffer(out));
        checked_("transform",
                 EVP_CipherUpdate
                 (&context_, buffer_cast<unsigned char *>(o), &outl,
                  buffer_cast<const unsigned char *>(i), buffer_size(i)));
        return *this;
      }

      /// Adds associated authenticated data, i.e. data which is accounted for in the authentication
      /// tag, but is not encrypted. Typically, this is used for associated meta data (like the
      /// packet header in a network protocol). This data must be added /before/ any message text is
      /// added to the cipher. The aad parameter can be any contiguous storage container that can be
      /// converted to the boost::asio::const_buffer using boost::asio::buffer.
      template<typename A>
      cipher &associate_data(const A &aad)
      {
        int outl;
        const_buffer buf(buffer(aad));
        size_t length(buffer_size(buf));
        const unsigned char *a(buffer_cast<const unsigned char *>(buf));
        if (length)
        {
          checked_("associated data", EVP_CipherUpdate(&context_, NULL, &outl, a, length));
        }
        return *this;
      }

      /// The encryption finalization routine. Populates the authentication tag "seal" that must be
      /// passed along for successful decryption. Any modifications in the cipher text or the
      /// associated data will be detected by the decryptor using this seal.

      /// The seal parameter can be any contiguous storage container that can be converted to the
      /// boost::asio::mutable_buffer using boost::asio::buffer.
      template<typename S>
      void seal(S &seal)
      {
        int outl;
        assert(encrypt_);
        mutable_buffer s(buffer(seal));
        checked_("seal", EVP_CipherFinal_ex(&context_, NULL, &outl));
        checked_("get tag",
                 EVP_CIPHER_CTX_ctrl
                 (&context_, EVP_CTRL_GCM_GET_TAG, buffer_size(s), buffer_cast<void *>(s)));
      }

      /// The decryption finalization routine. Uses the authentication tag to verify if the
      /// decryption was successful. If the tag verification fails an exception is thrown, if all is
      /// well, the method silently returns. If an exception is thrown, the decrypted data is
      /// corrupted and /must/ not be used.
      void verify()
      {
        int outl;
        assert(!encrypt_);
        checked_("verify", EVP_CipherFinal_ex(&context_, NULL, &outl));
      }

      ~cipher()
      {
        //EVP_CIPHER_CTX_cleanup(&context_);
      }
    private:
      bool encrypt_;
      EVP_CIPHER_CTX context_;
      void initialize(const_buffer key, const_buffer iv)
      {
        EVP_CIPHER_CTX_init(&context_);
        const unsigned char *i(buffer_cast<const unsigned char *>(iv));
        const unsigned char *k(buffer_cast<const unsigned char *>(key));
        checked_("initialize - i",
                 EVP_CipherInit_ex(&context_, EVP_aes_128_gcm(), NULL, NULL, NULL, encrypt_));
        checked_("set iv length",
                 EVP_CIPHER_CTX_ctrl(&context_, EVP_CTRL_GCM_SET_IVLEN, buffer_size(iv), NULL));
        checked_("initialize - ii",
                 EVP_CipherInit_ex(&context_, NULL, NULL, k, i, encrypt_));
      }
    };
  }
}
