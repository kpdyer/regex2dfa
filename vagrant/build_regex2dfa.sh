# build regex2dfa
export NPMBUILD=1
cd $BUILD_DIR
git clone $GIT_REGEX2DFA
cd $BUILD_DIR/regex2dfa/third_party/openfst
emconfigure ./configure --enable-bin --disable-shared --enable-static
emmake make
cd $BUILD_DIR/regex2dfa
emconfigure ./configure
emmake make -j$CORES npm/regex2dfa.js
