AC_INIT([regex2dfa],[0.0.1])

AC_CHECK_FILE(third_party/openfst/Makefile,
              [],
              cd third_party/openfst && ./configure --enable-bin --enable-static --disable-shared && cd ../..)

AC_CONFIG_FILES([Makefile])

AC_OUTPUT
