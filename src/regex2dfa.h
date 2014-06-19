#ifndef _REGEX2DFA_H
#define _REGEX2DFA_H

namespace regex2dfa {

bool Regex2Dfa(const std::string & regex,
               std::string * minimized_dfa);

} // namespace regex2dfa

#endif /* _REGEX2DFA_H */
