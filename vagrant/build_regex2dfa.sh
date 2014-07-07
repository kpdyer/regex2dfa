# build regex2dfa
export NPMBUILD=1
cd $BUILD_DIR
git clone $GIT_REGEX2DFA

cd $BUILD_DIR/regex2dfa/third_party/openfst
emconfigure ./configure --enable-bin --disable-shared --enable-static
emmake make
emconfigure ./configure --enable-bin --disable-shared --enable-static
emmake make -j$CORES

cd $BUILD_DIR/regex2dfa
rm npm/regex2dfa.js
emconfigure ./configure
emmake make npm/regex2dfa.js

cd $BULID_DIR
cp -rfv regex2dfa /vagrant
