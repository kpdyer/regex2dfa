#include <fstream>
#include <iostream>

#include "re2/re2.h"
#include "re2/regexp.h"
#include "re2/prog.h"

bool AttFstFromRegex(const std::string & regex, std::string * dfa) {
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
    (*dfa) = prog->PrintEntireDFA( re2::Prog::kFullMatch );
  } catch (int e) {
    // do nothing, we return the empty string
  }

  // cleanup
  if (prog!=NULL)
    delete prog;
  if (re!=NULL)
    re->Decref();

  return true;
}

bool AttFstMinimize(std::string & fst_path, std::string & str_dfa, std::string * minimized_dfa) {
  const char* temp_dir = getenv("TMPDIR");
  if (temp_dir == 0) {
    temp_dir = "/tmp";
  }
  std::string temp_dir_str = std::string(temp_dir);
  std::string temp_file = "000000";

  std::string abspath_dfa     = temp_dir_str+ "/" + temp_file + ".dfa";
  std::string abspath_fst     = temp_dir_str+ "/" + temp_file + ".fst";
  std::string abspath_fst_min = temp_dir_str+ "/" + temp_file + ".min.fst";
  std::string abspath_dfa_min = temp_dir_str+ "/" + temp_file + ".min.dfa";

  // write our input DFA to disk
  std::ofstream dfa_stream;
  dfa_stream.open (abspath_dfa.c_str());
  dfa_stream << str_dfa;
  dfa_stream.close();

  std::string cmd;

  // convert our ATT DFA string to an FST
  cmd = fst_path + "/fstcompile " + abspath_dfa + " " + abspath_fst;
  system(cmd.c_str());

  // convert our FST to a minmized FST
  cmd = fst_path + "/fstminimize " + abspath_fst + " " + abspath_fst_min;
  system(cmd.c_str());

  // covert our minimized FST to an ATT FST string
  cmd = fst_path + "/fstprint " + abspath_fst_min + " " + abspath_dfa_min;
  system(cmd.c_str());

  // read the contents of of the file at abspath_dfa_min to our retval
  std::ifstream dfa_min_stream(abspath_dfa_min.c_str());
  std::stringstream buffer;
  buffer << dfa_min_stream.rdbuf();
  dfa_min_stream.close();

  (*minimized_dfa) = std::string(buffer.str());

  // cleanup
  remove( abspath_dfa.c_str() );
  remove( abspath_fst.c_str() );
  remove( abspath_fst_min.c_str() );
  remove( abspath_dfa_min.c_str() );

  return true;
}

int
main (int argc, char **argv) {
  std::string fst_path = "third_party/openfst/src/bin";

  std::string dfa;
  AttFstFromRegex("^(a|b)$", &dfa);

  std::string minimized_dfa;
  AttFstMinimize(fst_path, dfa, &minimized_dfa);

  std::cout << minimized_dfa << std::endl;
}

