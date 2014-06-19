#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>

#include <iostream>

#include "regex2dfa.h"

int main (int argc, char **argv) {
  extern char *optarg;
  char *regex;
  int c;
  bool regex_set = false;
  std::string usage = "usage: %s -r REGEX\n";

  while ((c = getopt(argc, argv, "r:")) != -1)
    switch (c) {
    case 'r':
      regex = optarg;
      regex_set = true;
      break;
    }

  if (!regex_set) {
    std::cerr << usage << std::endl;
    exit(1);
  }

  std::string input_regex = std::string(regex);
  std::string minimized_dfa;

  bool success = regex2dfa::Regex2Dfa(input_regex, &minimized_dfa);
  if (success) {
    std::cout << minimized_dfa << std::endl;
  } else {
    std::cerr << "\033[1;31mERROR\033[0m";
    std::cerr << ": Failed to compile regex: \"" + input_regex + "\"";
    std::cerr << std::endl;
    return 1;
  }

  return 0;
}
