# build regex2dfa
cd $BUILD_DIR
git clone $GIT_REGEX2DFA
cd uTransformers
emconfigure ./configure
emmake make -j$CORES
