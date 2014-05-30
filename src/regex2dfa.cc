#include <stdio.h>
#include <getopt.h>

#include <iostream>

#include "re2/re2.h"
#include "re2/regexp.h"
#include "re2/prog.h"

int debug_flag, compile_flag, size_in_bytes;

std::string attFstFromRegex( const std::string regex )
{
    std::string retval;

    // specify compile flags for re2
    re2::Regexp::ParseFlags re_flags;
    re_flags = re2::Regexp::ClassNL;
    re_flags = re_flags | re2::Regexp::OneLine;
    re_flags = re_flags | re2::Regexp::PerlClasses;
    re_flags = re_flags | re2::Regexp::PerlB;
    re_flags = re_flags | re2::Regexp::PerlX;
    re_flags = re_flags | re2::Regexp::Latin1;

    re2::RegexpStatus status;

    // compile regex to DFA
    re2::Regexp* re = NULL;
    re2::Prog* prog = NULL;

    try {
        RE2::Options opt;
        re2::Regexp* re = re2::Regexp::Parse( regex, re_flags, &status );
        re2::Prog* prog = re->CompileToProg( opt.max_mem() );
        retval = prog->PrintEntireDFA( re2::Prog::kFullMatch );
    } catch (int e) {
        // do nothing, we return the empty string
    }

    // cleanup
    if (prog!=NULL)
        delete prog;
    if (re!=NULL)
        re->Decref();

    return retval;
}


int
main (int argc, char **argv)
{
std::cout << attFstFromRegex("^.+$");
  // Invokes ctor `GetOpt (int argc, char **argv, 
  //                       char *optstring);'
  //GetOpt getopt (argc, argv, "dcs:");
/*  char* regex;

    int option_index = 0;
  int option_char;
    static struct option long_options[] =
    {
        {"regex",  required_argument, 0, 'r'},
        {0, 0, 0, 0}
    };
  
  // Invokes member function `int operator ()(void);'
   while ((option_char = getopt_long (argc, argv, "d:i:",
                long_options, &option_index)  ) !=-1)
    switch (option_char)
      {  
         case 'r': regex = static_cast<char*>(optarg); break;
         case '?': fprintf (stderr, 
                            "usage: %s [dcs<size>]\n", argv[0]);
      }
*/
}

