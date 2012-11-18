#pragma once

#include <vector>
#include <string>
#include <iterator>
#include <stdexcept>
#include <type_traits>

#include <openssl/rand.h>

namespace ajd
{
  namespace crypto
  {
    /// A simple typedef for bytes
    typedef unsigned char byte;

    /// Algorithms for generating random bytes. The interface and implementation are the similar to
    /// std::generate_n and std::generate with the generator argument fixed to OpenSSL PRNG.

    /// _Effects_: generate invokes RAND_bytes and assigns the returned bytes through all the
    /// iterators in the range [first,last). generate_n does the same through all the iterators in
    /// the range [first,first + n) if n is positive, otherwise it does nothing.

    /// _Requires_: The iterator must belong to a container of ajd::crypto::byte

    /// _Returns_: generate_n returns `first + n`
    template<typename OutputIterator, typename Size>
    OutputIterator generate_n(OutputIterator first, Size n)
    {
      typedef typename std::iterator_traits<OutputIterator>::value_type input_type;
      static_assert(std::is_same<byte, input_type>::value, "only works with bytes");

      if (n > 0)
      {
        std::vector<byte> bytes(n);
        if (RAND_bytes(&bytes[0], n) == 0)
        {
          throw std::runtime_error("random number generator failed.");
        }
        first = std::copy_n(bytes.begin(), n, first);
      }
      return first;
    }

    template<typename ForwardIt>
    void generate(ForwardIt first, ForwardIt last)
    {
      generate_n(first, std::distance(first, last));
    }
  }
}
