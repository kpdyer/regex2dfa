# build regex2dfa
export NPMBUILD=1
cd $BUILD_DIR
git clone $GIT_REGEX2DFA
cd regex2dfa
emconfigure ./configure
emmake make -j$CORES
