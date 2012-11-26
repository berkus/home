#pragma once

#include <vector>
#include <cassert>
#include <stdexcept>

#include <openssl/evp.h>
#include <openssl/rand.h>

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

    bool random_ok() { return RAND_status() == 1; }

    void random(mutable_buffer b)
    {
      if (!RAND_bytes(buffer_cast<unsigned char *>(b), buffer_size(b)))
      {
        throw std::runtime_error("random number generation failed");
      }
    }

    class cipher : boost::noncopyable
    {
    public:
      enum mode { encrypt, decrypt };

      cipher(mode m, const_buffer key, const_buffer iv): mode_(m)
      {
        assert(buffer_size(key) == 16);
        assert(buffer_size(key) == buffer_size(iv));
        const unsigned char *i(buffer_cast<const unsigned char *>(iv));
        const unsigned char *k(buffer_cast<const unsigned char *>(key));

        EVP_CIPHER_CTX_init(&ctx_);
        if (!
            (
              mode_ == encrypt ?
              EVP_EncryptInit_ex(&ctx_, EVP_aes_128_ctr(), NULL, k, i)
              :
              EVP_DecryptInit_ex(&ctx_, EVP_aes_128_ctr(), NULL, k, i)
            )
           )
        {
          EVP_CIPHER_CTX_cleanup(&ctx_);
          throw std::runtime_error("random number generation failed");
        }
      }

      void transform(const_buffer in_buffer, mutable_buffer out_buffer)
      {
        int outl;
        int inl(buffer_size(in_buffer));
        unsigned char *out(buffer_cast<unsigned char *>(out_buffer));
        const unsigned char *in(buffer_cast<const unsigned char *>(in_buffer));
        if (!
            (
              mode_ == encrypt ?
              EVP_EncryptUpdate(&ctx_, out, &outl, in, inl)
              :
              EVP_DecryptUpdate(&ctx_, out, &outl, in, inl)
            )
           )
        {
          throw std::runtime_error("random number generation failed");
        }
      }

      ~cipher()
      {
        EVP_CIPHER_CTX_cleanup(&ctx_);
      }

    private:
      mode mode_;
      EVP_CIPHER_CTX ctx_;
    };
  }
}
