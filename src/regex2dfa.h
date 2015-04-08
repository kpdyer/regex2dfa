#ifndef _REGEX2DFA_H
#define _REGEX2DFA_H

#include <string>

namespace regex2dfa {

bool Regex2Dfa(const std::string & regex,
               std::string * minimized_dfa);

} // namespace regex2dfa

#endif /* _REGEX2DFA_H */
