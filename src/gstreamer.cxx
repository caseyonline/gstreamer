#include <stdio.h>
#include <iostream>

#include "test.hxx"

using namespace std;

int main(int ac, char* av[]) {

  if (ac < 2)
    cout << "gstreamer <test num>" << endl;

  else
  switch( atoi(av[1]) )
  {
    case 1:
      test1(ac, av);
      break;

    case 2:
      test2(ac, av);
      break;

    default:
      cout << "undefined test" << endl;
  }
}
