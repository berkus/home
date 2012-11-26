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
