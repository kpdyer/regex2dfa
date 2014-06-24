# https://github.com/kripken/emscripten/wiki/LLVM-Backend
cd $BUILD_DIR
git clone $GIT_EMSCRIPTEN
cd emscripten
git checkout $EMSCRIPTEN_VERSION
cd ..
git clone $GIT_EMSCRIPTEN_FASTCOMP
cd emscripten-fastcomp
git checkout $EMSCRIPTEN_VERSION
cd tools
git clone $GIT_EMSCRIPTEN_FASTCOMP_CLANG clang
cd clang
git checkout $EMSCRIPTEN_VERSION
cd ..
cd ..
./configure --prefix=$INSTALL_DIR --enable-optimized --disable-assertions --enable-targets=host,js
make -j$CORES

# init emscripten
$BUILD_DIR/emscripten/emcc

# fix broken emar
#  - using emar provided by emscripten results in archives that cause llvm-nm to hang
sudo rm $BUILD_DIR/emscripten/emar
sudo ln -s /usr/bin/ar $BUILD_DIR/emscripten/emar
