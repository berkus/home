#include "executor.h"
#include <gtest/gtest.h>

void work() {}
void other_work(const char *c) {}
struct functor_work { void operator()() {} };
auto lambda = [] {};

TEST(Executor, UsageSyntax)
{
  ajd::executor e(2);
  e.submit(work);
  e.submit(boost::bind(other_work, "input"));
  e.submit(functor_work());
  e.submit(lambda);
}
