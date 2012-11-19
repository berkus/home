#include "crypto.h"

#include <array>
#include <cassert>
#include <iostream>
#include <algorithm>

void test_random_generator()
{
  // see if we have enough randomness.
  assert(ajd::crypto::random_ok() == true);

  // generate a random AES-128 key.
  ajd::crypto::byte key[16];
  ajd::crypto::generate_random_n(key, 16);

  // generate a random 64 bit nonce.
  std::vector<ajd::crypto::byte> nonce(8);
  ajd::crypto::generate_random(nonce.begin(), nonce.end());

  std::cout << "random passed" << std::endl;
}

int main()
{
  test_random_generator();
}
