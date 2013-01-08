#include "crypto.h"
#include <cassert>
#include <algorithm>
#include <sstream>

void unhexlify(const std::string &hex, std::vector<unsigned char> &bytes)
{
  for (std::size_t i = 0; i < hex.size(); i += 2)
  {
    int byte;
    std::stringstream ss;
    ss << std::hex << hex[i] << hex[i + 1];
    ss >> byte;
    bytes.push_back(byte);
  }
}

void pbkdf_tests()
{
  // test data from: http://tools.ietf.org/html/rfc6070 (ignoring the really slow one c=16777216)
  // expected values from: http://stackoverflow.com/questions/5130513/pbkdf2-hmac-sha2-test-vectors
  using namespace ajd;

  struct test
  {
    int c;               // iteration count
    int dkLen;           // derived key length
    std::string P;       // password
    std::string S;       // salt
    std::string DK;      // expected output: derived key
  } tests[5];

  tests[0].c = 1;
  tests[0].dkLen = 32;
  tests[0].S = "salt";
  tests[0].P = "password";
  tests[0].DK = "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b";

  tests[1].c = 2;
  tests[1].dkLen = 32;
  tests[1].S = "salt";
  tests[1].P = "password";
  tests[1].DK = "ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43";

  tests[2].c = 4096;
  tests[2].dkLen = 32;
  tests[2].S = "salt";
  tests[2].P = "password";
  tests[2].DK = "c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a";

  tests[3].c = 4096;
  tests[3].dkLen = 40;
  tests[3].S = "saltSALTsaltSALTsaltSALTsaltSALTsalt";
  tests[3].P = "passwordPASSWORDpassword";
  tests[3].DK = "348c89dbcbd32b2f32d814b8116e84cf2b17347ebc1800181c4e2a1fb8dd53e1c635518c7dac47e9";

  tests[4].c = 4096;
  tests[4].dkLen = 16;
  tests[4].S = std::string("sa\0lt", 5);
  tests[4].P = std::string("pass\0word", 9);
  tests[4].DK = "89b69d0516f829893c696226650a8687";

  for (int i = 0; i < 5; i++)
  {
    std::vector<unsigned char> expected;
    std::vector<unsigned char> key(tests[i].dkLen);
    unhexlify(tests[i].DK, expected);
    crypto::derive_key(key, tests[i].P, tests[i].S, tests[i].c);
    assert(std::equal(expected.begin(), expected.end(), key.begin()));
  }
}

int main()
{
  pbkdf_tests();
}
