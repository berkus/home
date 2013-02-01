/// Copyright (c) 2013, Aldrin's Notebook.
#include "executor.h"
#include <iostream>

using namespace ajd;

void foo(){
  std::cout<< "hello\n";
}

int main()
{
  executor::async svc;
  svc.submit(foo);
}
