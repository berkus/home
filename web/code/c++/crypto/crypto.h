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
    /// Checks if the underlying crypto system has seeded its PRNG sufficiently. If this method
    /// returns false, you should consider using OpenSSL RAND_add to seed the PRNG.

    /// _Returns_: true if the underlying PRNG is good to go.
    bool random_ok() { return RAND_status() == 1; }

    /// Algorithms for generating random bytes. The interface and implementation are the similar to
    /// std::generate_random_n and std::generate_random with the generator argument fixed to OpenSSL
    /// PRNG.

    /// _Effects_: generate_random invokes RAND_bytes and assigns the returned bytes through all the
    /// iterators in the range [first,last). generate_random_n does the same through all the
    /// iterators in the range [first,first + n) if n is positive, otherwise it does nothing.

    /// _Requires_: The iterator must belong to a container of unsigned char

    /// _Returns_: generate_random_n returns `first + n`
    template<typename OutputIterator, typename Size>
    OutputIterator generate_random_n(OutputIterator first, Size n)
    {
      typedef typename std::iterator_traits<OutputIterator>::value_type input_type;
      static_assert(std::is_same<unsigned char, input_type>::value, "value type needs to be unsigned char");

      if (n > 0)
      {
        std::vector<unsigned char> bytes(n);
        if (RAND_bytes(&bytes[0], n) == 0)
        {
          throw std::runtime_error("random number generation failed");
        }
        first = std::copy_n(bytes.begin(), n, first);
      }
      return first;
    }

    template<typename ForwardIt>
    void generate_random(ForwardIt first, ForwardIt last)
    {
      generate_random_n(first, std::distance(first, last));
    }
  }
}
