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

  for (int i = 0; i < sizeof(tests) / sizeof(struct test); i++)
  {
    std::vector<unsigned char> expected;
    std::vector<unsigned char> key(tests[i].dkLen);
    unhexlify(tests[i].DK, expected);
    crypto::derive_key(key, tests[i].P, tests[i].S, tests[i].c);
    assert(std::equal(expected.begin(), expected.end(), key.begin()));
  }
}

void sha256_tests()
{
  // test vectors from: http://csrc.nist.gov/groups/STM/cavp/index.html#03
  // only a few test cases were chosen. we're only doing sanity tests here.
  // in particular, we've chosen Len=0, 8, 64, 512 from SHA256ShortMsg.rsp
  using namespace ajd;

  struct test
  {
    std::string Msg;     // message
    std::string MD;      // digest
  } tests[4];

  tests[0].Msg = "";
  tests[0].MD = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

  tests[1].Msg = "d3";
  tests[1].MD = "28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1";

  tests[2].Msg = "5738c929c4f4ccb6";
  tests[2].MD = "963bb88f27f512777aab6c8b1a02c70ec0ad651d428f870036e1917120fb48bf";

  tests[3].Msg = "5a86b737eaea8ee976a0a24da63e7ed7eefad18a101c1211e2b3650c5187c2a\
8a650547208251f6d4237e661c7bf4c77f335390394c37fa1a9f9be836ac28509";
  tests[3].MD = "42e61e174fbb3897d6dd6cef3dd2802fe67b331953b06114a65c772859dfc1aa";

  crypto::hash md;

  for (int i = 0; i < sizeof(tests) / sizeof(struct test); i++)
  {
    std::vector<unsigned char> message;
    std::vector<unsigned char> expected;
    unhexlify(tests[i].Msg, message);
    unhexlify(tests[i].MD, expected);
    md.update(message);
    crypto::hash::value value(md.finalize());
    assert(std::equal(expected.begin(), expected.end(), value.begin()));
  }
}

void hmac_tests()
{
  // test data from https://tools.ietf.org/html/rfc4231
  using namespace ajd;

  struct test
  {
    std::string Key;
    std::string Data;
    std::string MAC;
  } tests[6];

  tests[0].Key = "0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b";
  tests[0].Data = "4869205468657265";
  tests[0].MAC = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7";

  tests[1].Key = "4a656665";
  tests[1].Data = "7768617420646f2079612077616e7420666f72206e6f7468696e673f";
  tests[1].MAC = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843";

  tests[2].Key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
  tests[2].Data = "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\
dddddddddddddddddddddddddddddddd";
  tests[2].MAC = "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe";

  tests[3].Key = "0102030405060708090a0b0c0d0e0f10111213141516171819";
  tests[3].Data = "cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd\
cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd";
  tests[3].MAC = "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b";

  tests[4].Key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaa";
  tests[4].Data = "54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a\
65204b6579202d2048617368204b6579204669727374";
  tests[4].MAC = "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54";

  tests[5].Key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaa";
  tests[5].Data = "5468697320697320612074657374207573696e672061206c6172676572207468\
616e20626c6f636b2d73697a65206b657920616e642061206c61726765722074\
68616e20626c6f636b2d73697a6520646174612e20546865206b6579206e6565\
647320746f20626520686173686564206265666f7265206265696e6720757365\
642062792074686520484d414320616c676f726974686d2e";
  tests[5].MAC = "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2";

  for (int i = 0; i < sizeof(tests) / sizeof(struct test); i++)
  {
    std::vector<unsigned char> key;
    std::vector<unsigned char> data;
    std::vector<unsigned char> expected;
    unhexlify(tests[i].Key, key);
    unhexlify(tests[i].Data, data);
    unhexlify(tests[i].MAC, expected);
    crypto::hash h(key);
    assert(std::equal(expected.begin(), expected.end(), h.update(data).finalize().begin()));
  }
}

int main()
{
  hmac_tests();
  pbkdf_tests();
  sha256_tests();
}
