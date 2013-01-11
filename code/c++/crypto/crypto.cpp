#include "crypto.h"
#include <cassert>
#include <boost/array.hpp>
#include <boost/shared_array.hpp>

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

void key_generation()
{
  using namespace ajd;
  crypto::symmetric_key key;
  boost::array<unsigned char, 16> salt;
  crypto::fill_random(salt);  // random salt.
  crypto::derive_key(key, "password", salt); // password derived key.
}

void message_digest()
{
  using namespace ajd;
  crypto::hash md;                        // the hash object
  md.update("hello");                     // add data
  md.update("world");                     // more data
  crypto::hash::value sha(md.finalize()); // get the hash
  assert(sha[0] == '\r');                 // avoid unused-variable warning.
}

void message_authentication_code()
{
  using namespace ajd;
  crypto::symmetric_key key;               // the hash key
  crypto::derive_key(key, "pass", "salt"); // password derived key.
  crypto::hash h(key);                     // the keyed-hash object
  h.update("hello");                       // add data
  h.update("world");                       // more data
  crypto::hash::value mac(h.finalize());   // get the mac
  assert(mac[0] == '\r');                  // avoid unused-variable warning.
}

int main()
{
  random_generation();
  key_generation();
  message_digest();
}

// void test_transform()
// {
//   // initialize key and IV
//   unsigned char iv[16];
//   unsigned char key[16];
//   crypto::random(crypto::buffer(iv));
//   crypto::random(crypto::buffer(key));

//   // the message
//   std::string message("can you keep a secret?");

//   // encipher
//   std::vector<unsigned char> encrypted(message.size());
//   crypto::encipher encryptor(crypto::buffer(key), crypto::buffer(iv));
//   encryptor.transform(crypto::buffer(message), crypto::buffer(encrypted));

//   // decipher
//   std::vector<unsigned char> decrypted(message.size());
//   crypto::decipher decryptor(crypto::buffer(key), crypto::buffer(iv));
//   decryptor.transform(crypto::buffer(encrypted), crypto::buffer(decrypted));

//   // sanity test
//   assert(message == std::string(decrypted.begin(), decrypted.end()));
// }

// // See F.5.1 in http://csrc.nist.gov/publications/nistpubs/800-38a/sp800-38a.pdf
// void test_nist_encrypt_vector()
// {
//   unsigned char key[16] =
//   {
//     0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
//     0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
//   };

//   unsigned char iv[16] =
//   {
//     0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7,
//     0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff
//   };

//   unsigned char plaintext[64] =
//   {
//     0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96,
//     0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a,
//     0xae, 0x2d, 0x8a, 0x57, 0x1e, 0x03, 0xac, 0x9c,
//     0x9e, 0xb7, 0x6f, 0xac, 0x45, 0xaf, 0x8e, 0x51,
//     0x30, 0xc8, 0x1c, 0x46, 0xa3, 0x5c, 0xe4, 0x11,
//     0xe5, 0xfb, 0xc1, 0x19, 0x1a, 0x0a, 0x52, 0xef,
//     0xf6, 0x9f, 0x24, 0x45, 0xdf, 0x4f, 0x9b, 0x17,
//     0xad, 0x2b, 0x41, 0x7b, 0xe6, 0x6c, 0x37, 0x10
//   };

//   unsigned char expected[64] =
//   {
//     0x87, 0x4d, 0x61, 0x91, 0xb6, 0x20, 0xe3, 0x26,
//     0x1b, 0xef, 0x68, 0x64, 0x99, 0x0d, 0xb6, 0xce,
//     0x98, 0x06, 0xf6, 0x6b, 0x79, 0x70, 0xfd, 0xff,
//     0x86, 0x17, 0x18, 0x7b, 0xb9, 0xff, 0xfd, 0xff,
//     0x5a, 0xe4, 0xdf, 0x3e, 0xdb, 0xd5, 0xd3, 0x5e,
//     0x5b, 0x4f, 0x09, 0x02, 0x0d, 0xb0, 0x3e, 0xab,
//     0x1e, 0x03, 0x1d, 0xda, 0x2f, 0xbe, 0x03, 0xd1,
//     0x79, 0x21, 0x70, 0xa0, 0xf3, 0x00, 0x9c, 0xee
//   };

//   unsigned char ciphertext[64];
//   crypto::encipher encryptor(crypto::buffer(key), crypto::buffer(iv));
//   encryptor.transform(crypto::buffer(plaintext), crypto::buffer(ciphertext));
//   assert(std::equal(expected, expected + 64, ciphertext));
// }
