#include "crypto.h"

#include <array>
#include <iostream>
#include <algorithm>

void generate_random_bytes()
{
  // generate a random AES-128 key.
  std::array<ajd::crypto::byte, 16> aes128_key;
  ajd::crypto::generate(aes128_key.begin(), aes128_key.end());

  // generate a random 64 bit nonce.
  std::vector<ajd::crypto::byte> nonce(8);
  ajd::crypto::generate_n(nonce.begin(), 8);
}

int main()
{
  generate_random_bytes();
}
