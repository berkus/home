#include <cstddef>
#include <cassert>
#include <iostream>
using namespace std;

namespace cstddef
{
  void try_offsetof()
  {
    struct A { int a; char b; float c;};
    assert(offsetof(A, a) == 0);
    assert(offsetof(A, b) == sizeof(int));
    assert(offsetof(A, c) == 8);
  }
}

int main()
{
  cstddef::try_offsetof();
}
