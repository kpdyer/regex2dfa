import cRegex2dfa

def regex2dfa(regex):
    regex = "^" + regex + "$"
    return cRegex2dfa.regex2dfa(regex)
