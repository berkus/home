#include "executor.h"

void work() {}
void other_work(const char *c) {}
struct functor_work { void operator()() {} };

void executor_usage()
{
  ajd::executor e(2);
  e.submit(work);
  e.submit(boost::bind(other_work, "input"));
  e.submit(functor_work());
}

int main()
{
  executor_usage();
}
