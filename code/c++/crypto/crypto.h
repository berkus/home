/// Copyright (c) 2013, Aldrin's Notebook (http://aldrin.co). All rights reserved.
/// Licensed under the BSD-2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

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

    /// Check return values from OpenSSL and throw an exception if it failed.
    /// @param what the logical operation being performed
    /// @success the return value from OpenSSL API
    void checked_(const char *what, int ret)
    {
      if (ret == 0)
      {
        std::string message(what);
        message += " failed.";
        throw std::runtime_error(message);
      }
    }

    /// Remove sensitive data from the buffer
    template<typename C> void cleanse(C &c)
    {
      mutable_buffer b(buffer(c));
      OPENSSL_cleanse(buffer_cast<void *>(b), buffer_size(b));
    }

    /// A convenience typedef for a 128 bit block.
    typedef boost::array<unsigned char, 16> block;

    /// Checks if the  underlying PRNG is sufficiently seeded. In  the (exceptional) situation where
    /// this check  returns 'false', you  /must/ use the  OpenSSL seed routines  RAND_seed, RAND_add
    /// directly to add entropy to the underlying PRNG.
    bool prng_ok() { return RAND_status() == 1; }

    /// Fills the passed container with random bytes.
    /// @param c  (output) container populated with random bits
    template<typename C> void fill_random(C &c)
    {
      mutable_buffer b(buffer(c));
      checked_("random bytes", RAND_bytes(buffer_cast<unsigned char *>(b), buffer_size(b)));
    }

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
    {
      const_buffer p(buffer(passwd));
      int passlen(buffer_size(p));
      const char *pass(buffer_cast<const char *>(p));

      const_buffer s(buffer(salt));
      int saltlen(buffer_size(s));
      const unsigned char *slt(buffer_cast<const unsigned char *>(s));

      mutable_buffer k(buffer(key));
      int keylen(buffer_size(k));
      unsigned char *out(buffer_cast<unsigned char *>(k));

      checked_("key derivation",
               PKCS5_PBKDF2_HMAC(pass, passlen, slt, saltlen, c, EVP_sha256(), keylen, out));
    }

    /// Generates a keyed or a plain cryptographic hash.
    class hash: boost::noncopyable
    {
    public:
      /// A convenience typedef for a 256 SHA-256 value.
      typedef boost::array<unsigned char, 32> value;

      /// The plain hash constructor. Initializes the underlying hash context.
      hash(): keyed_(false), digest_(EVP_sha256()), md_context_(EVP_MD_CTX_create())
      {
        checked_("digest initialization", EVP_DigestInit_ex(md_context_, digest_, NULL));
      }

      /// The keyed hash constructor. Initializes the underlying hash context.
      /// @param key (input) container holding the secret key
      template<typename C>
      hash(const C &key): keyed_(true), digest_(EVP_sha256())
      {
        HMAC_CTX_init(&hmac_context_);
        const_buffer key_buffer(buffer(key));
        int key_length(buffer_size(key_buffer));
        const void *k(buffer_cast<const void *>(key_buffer));
        checked_("mac initialization", HMAC_Init_ex(&hmac_context_, k, key_length, digest_, NULL));
      }

      /// Add the  contents of the passed  container to the  underlying context. This method  can be
      /// invoked multiple times to add all the data that needs to be hashed.
      /// @param data (input) container holding the input data
      template <typename C>
      hash &update(const C &data)
      {
        const_buffer b(buffer(data));
        int l(buffer_size(b));
        const void *d(buffer_cast<const void *>(b));
        checked_("add data to hash",
                 (keyed_ ?
                  HMAC_Update(&hmac_context_, (const unsigned char *)d, l)
                  : EVP_DigestUpdate(md_context_, d, l)));
        return *this;
      }

      /// Get the  resultant hash value. This  method also reinitializes the  underlying context, so
      /// the same instance can be reused to compute more hashes.
      /// @param sha (output) container populated with the hash/mac bits
      template<typename C>
      void finalize(C &sha)
      {
        mutable_buffer b(buffer(sha));
        unsigned char *d(buffer_cast<unsigned char *>(b));
        checked_("finalization of hash",
                 (keyed_ ?
                  HMAC_Final(&hmac_context_, d, 0)
                  : EVP_DigestFinal_ex(md_context_, d, NULL)));
        checked_("reinitialization of hash",
                 (keyed_ ?
                  HMAC_Init_ex(&hmac_context_, NULL, 0, NULL, NULL)
                  : EVP_DigestInit_ex(md_context_, digest_, NULL)));
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
      /// Encryption mode  constructor, only takes key  and IV parameters.  Initializes the instance
      /// for encryption. The  key should be 128  bit (since we're with AES-128).  Typically, the IV
      /// should be 128 bit IV too but GCM supports  other IV sizes, so those can be passed to.
      /// @param key (input) container holding 128 key bits (use crypto::block)
      /// @param iv  (input) container holding 128 initialization vector bits (use crypto::block)
      template<typename K, typename I>
      cipher(const K &key, const I &iv): encrypt_(true)
      {
        initialize(buffer(key), buffer(iv));
      }

      /// Decryption  mode constructor,  takes key,  IV and  the authentication  tag  as parameters.
      /// Initializes  the cipher  for  decryption and  sets  the passed  tag  up for  authenticated
      /// decryption. The key  and IV should be the  same that were used to  generate the ciphertext
      /// you're trying to decrypt (obviously). The seal parameter should contain the authentication
      /// tag returned by the 'seal' call after encryption.
      /// @param key  (input) container holding 128 key bits (use crypto::block)
      /// @param iv   (input) container holding 128 initialization vector bits (use crypto::block)
      /// The seal parameter does not have a 'const' with it because of the OpenSSL API.
      /// @param seal (input) container holding 128 authentication tag bits (use crypto::block)
      template<typename K, typename I, typename S>
      cipher(const K &key, const I &iv, S &seal): encrypt_(false)
      {
        initialize(buffer(key), buffer(iv));

        mutable_buffer b(buffer(seal));
        int tag_length(buffer_size(b));
        void *tag(buffer_cast<void *>(b));
        checked_("set tag", EVP_CIPHER_CTX_ctrl(&context_, EVP_CTRL_GCM_SET_TAG, tag_length, tag));
      }

      /// The  cipher transformation  routine. This  encrypts or  decrypts the  bytes from  the 'in'
      /// buffer and places them into the 'out'  buffer.  Since GCM does not require any padding the
      /// output buffer size  should be the same  as the input.  If you  have unencrypted associated
      /// data that must be added using 'associate_data' first.
      /// @param input  (input)  plaintext or ciphertext (for encryption or decryption resp.)
      /// @param output (output) inverse of the input
      template<typename I, typename O>
      cipher &transform(const I &input, O &output)
      {
        int outl;
        const_buffer i(buffer(input));
        mutable_buffer o(buffer(output));
        int input_length(buffer_size(i));
        unsigned char *out(buffer_cast<unsigned char *>(o));
        const unsigned char *in(buffer_cast<const unsigned char *>(i));
        checked_("transform", EVP_CipherUpdate(&context_, out, &outl, in, input_length));
        return *this;
      }

      /// Adds associated authenticated data, i.e. data which is accounted for in the authentication
      /// tag, but  is not encrypted.  Typically, this  is used for  associated meta data  (like the
      /// packet header in a network protocol). This data must be added /before/ any message text is
      /// added to the cipher.
      /// @param aad (input) container with associated data
      template<typename A>
      cipher &associate_data(const A &aad)
      {
        int outl;
        const_buffer buf(buffer(aad));
        int aad_length(buffer_size(buf));
        const unsigned char *a(buffer_cast<const unsigned char *>(buf));
        if (aad_length)
        {
          checked_("associated data", EVP_CipherUpdate(&context_, NULL, &outl, a, aad_length));
        }
        return *this;
      }

      /// The encryption finalization routine. Populates  the authentication tag "seal" that must be
      /// passed  along for  successful decryption.   Any modifications  in the  cipher text  or the
      /// associated data will be detected by the decryptor using this seal.
      /// @param seal (output) container to be populated with the tag bits
      template<typename S>
      void seal(S &seal)
      {
        int outl;
        assert(encrypt_);
        mutable_buffer s(buffer(seal));
        int tag_length(buffer_size(s));
        void *tag(buffer_cast<void *>(s));
        checked_("seal", EVP_CipherFinal_ex(&context_, NULL, &outl));
        checked_("get tag", EVP_CIPHER_CTX_ctrl(&context_, EVP_CTRL_GCM_GET_TAG, tag_length, tag));
      }

      /// The  decryption  finalization  routine. Uses  the  authentication  tag  to verify  if  the
      /// decryption was successful. If the tag verification fails an exception is thrown, if all is
      /// well,  the method silently  returns.  If  an exception  is thrown,  the decrypted  data is
      /// corrupted and /must/ not be used.
      void verify()
      {
        int outl;
        assert(!encrypt_);
        checked_("verify", EVP_CipherFinal_ex(&context_, NULL, &outl));
      }

      ~cipher()
      {
        EVP_CIPHER_CTX_cleanup(&context_);
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
