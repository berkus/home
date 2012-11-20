#include "crypto.h"

#include <array>
#include <cassert>
#include <iostream>
#include <algorithm>

void test_random_generator()
{
  using ajd::crypto::random_ok;
  using ajd::crypto::generate_random;
  using ajd::crypto::generate_random_n;

  // see if we have enough randomness.
  assert(random_ok() == true);

  // generate an AES-128 key.
  unsigned char key[16];
  generate_random_n(key, 16);

  // generate a random 64 bit nonce.
  std::vector<unsigned char> nonce(8);
  generate_random(nonce.begin(), nonce.end());

  std::cout << "random passed" << std::endl;
}

int main()
{
  test_random_generator();
}
