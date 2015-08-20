from os.path import abspath, dirname, join

from cffi import FFI


regex2dfa_header = abspath(join(dirname(__file__), 'src', 'regex2dfa.h'))

ffi = FFI()

ffi.cdef(
    """
    const char * cffi_regex2dfa(char *regex);
    void free(void *ptr);
    """
)

ffi.set_source(
    '_regex2dfa',
    """
    #include "%s"

    extern "C" {
        extern const char * cffi_regex2dfa(char *regex) {
            const std::string input_regex = std::string(regex);

            std::string minimized_dfa;

            regex2dfa::Regex2Dfa(input_regex, &minimized_dfa);
            return strdup(minimized_dfa.c_str());
        }
    }
    """ % regex2dfa_header,
    source_extension='.cpp',
    library_dirs=['.libs'],
    libraries=['regex2dfa'],
    extra_compile_args=[
        '-O3',
        '-fstack-protector-all',
        '-D_FORTIFY_SOURCE',
        '-fPIC',
    ],
)


if __name__ == '__main__':
    ffi.compile()
