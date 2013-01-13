#include "crypto.h"
#include <cassert>
#include <boost/array.hpp>
#include <boost/shared_array.hpp>

using namespace ajd;

void random_generation()
{
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
  crypto::block salt;
  crypto::block key;
  crypto::fill_random(salt);  // random salt.
  crypto::derive_key(key, "password", salt); // password derived key.
}

void message_digest()
{
  crypto::hash md;                        // the hash object
  md.update("hello");                     // add data
  md.update("world");                     // more data
  crypto::hash::sha256 sha(md.finalize()); // get the hash
  assert(sha[0] == '\r');                 // avoid unused-variable warning.
}

void message_authentication_code()
{
  crypto::block key;               // the hash key
  crypto::derive_key(key, "pass", "salt"); // password derived key
  crypto::hash h(key);                     // the keyed-hash object
  h.update("hello");                       // add data
  h.update("world");                       // more data
  crypto::hash::sha256 mac(h.finalize());   // get the mac
  assert(mac[0] == '\r');                  // avoid unused-variable warning
}

void encryption()
{
  crypto::block iv;
  crypto::block key;
  crypto::block seal;

  crypto::fill_random(iv);
  crypto::fill_random(key);
  std::string text("can you keep a secret?");

  std::vector<unsigned char> ciphertext(text.size());
  {
    crypto::cipher cipher(key, iv);
    cipher.transform(text, ciphertext);
    cipher.seal(seal);
  }

  std::vector<unsigned char> decrypted(ciphertext.size());
  {
    crypto::cipher cipher(key, iv, seal);
    cipher.transform(ciphertext, decrypted);
    cipher.verify();
  }

  assert(std::equal(text.begin(), text.end(), decrypted.begin()));
}

int main()
{
  ERR_load_crypto_strings();
  random_generation();
  key_generation();
  message_digest();
  encryption();
  ERR_free_strings();
}
