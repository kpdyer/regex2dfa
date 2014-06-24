# build regex2dfa
export NPMBUILD=1
cd $BUILD_DIR
git clone $GIT_REGEX2DFA
cd uTransformers
emconfigure ./configure
emmake make -j$CORES
