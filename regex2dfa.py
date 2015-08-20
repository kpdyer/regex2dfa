from _regex2dfa import ffi, lib


def regex2dfa(regex):
    regex = '^' + regex + '$'

    # We use strdup() to get a copy of the minimized DFA, so we need to free
    # the C string ourselves.
    c_dfa = lib.cffi_regex2dfa(regex)
    dfa = ffi.string(c_dfa)
    lib.free(c_dfa)

    return dfa
