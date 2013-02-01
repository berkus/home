/// Copyright (c) 2013, Aldrin's Notebook.
#pragma once

#include <future>

namespace ajd
{
  namespace executor
  {
    class async
    {
    public:
      template <typename T>
      auto submit(T t) -> std::future<decltype(t())>
      {
        return std::async(t);
      }
    };

    class singlethreaded;
    class fixed_threadpool;
    class scheduled_threadpool;
    class scheduled_singlethreaded;
  }
}
