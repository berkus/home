#include "executor.h"

#define BOOST_TEST_MODULE Executor
#include <boost/test/unit_test.hpp>

void work() {}
void other_work(const char *c) {}
struct functor_work { void operator()() {} };

BOOST_AUTO_TEST_CASE(UsageSyntax)
{
  ajd::executor e(2);
  e.submit(work);
  e.submit(boost::bind(other_work, "input"));
  e.submit(functor_work());
}
