Title: Thread-Pool Executor using Boost.ASIO
Tags:  C++, Boost
Date:  07/09/2011
Slug:  asio_executor

Consider the problem of writing a thread pool executor: i.e. an abstraction that takes arbitrary
user defined tasks and executes them concurrently over a pool of threads. Here's a (slightly
overweight) [example][java] of the abstraction from `java.util.concurrent`. In this note, I describe
another (lean) implementation using a few bits from the treasure trove of [Boost.ASIO][asio].

[Here's][test] what I expect from the executor (syntactically):

```` c++
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
````

I expect to create an executor with the specified number of threads in its pool and to have it ready
to jobs that I submit during the lifetime of the instance. The destructor must wait till the last
submitted job is completed and then clean up everything. As far as the tasks go, anything that is
invokable must be acceptable.

With those requirements in mind, [here][impl]'s an complete implementation:

```` c++
#ifndef AJD_EXECUTOR_H_
#define AJD_EXECUTOR_H_

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/thread.hpp>

namespace ajd
{
  using boost::bind;
  using boost::thread;
  using boost::thread_group;
  using boost::asio::io_service;

  class executor
  {
  public:

    executor(size_t n): service_(n), work_(service_)
    {
      for (size_t i = 0; i < n; i++)
      { pool_.create_thread(bind(&io_service::run, &service_)); }
    }

    ~executor()
    {
      service_.stop();
      pool_.join_all();
    }

    template<typename F> void submit(F task)
    {
      service_.post(task);
    }

  protected:
    thread_group pool_;
    io_service service_;
    io_service::work work_;
  };
}

#endif // AJD_EXECUTOR_H_
````

As someone who has written shabbily stitched executors in the past, I can't help but marvel at the
economy of this implementation. No dispatch queues, no mutexes to guard share state, no condition
variables to signal job arrivals, no shutdown flags, no nothing. Just the neat, power-packed
=asio::io_service= facade and we're done. Of course, there's still quite a bit left before we use
this in a complete application, but how cool is that for a start?

[asio]: http://www.boost.org/doc/libs/1_47_0/doc/html/boost_asio.html    
[impl]: https://github.com/aldrin/home/blob/master/web/code/c++/boost/executor_test.h
[test]: https://github.com/aldrin/home/blob/master/web/code/c++/boost/executor_test.cc
[java]: http://download.oracle.com/javase/6/docs/api/java/util/concurrent/ThreadPoolExecutor.html        
