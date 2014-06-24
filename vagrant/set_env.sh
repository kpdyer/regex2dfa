export WORKING_DIR=/home/vagrant
export BUILD_DIR=$WORKING_DIR/build
export INSTALL_DIR=$WORKING_DIR/install
export PATH=$INSTALL_DIR/bin:$BUILD_DIR/emscripten-fastcomp/Release/bin:$BUILD_DIR/emscripten:$PATH

export GIT_REGEX2DFA=https://github.com/kpdyer/regex2dfa.git

export CORES=`nproc`

export LLVM=$BUILD_DIR/emscripten-fastcomp/Release/bin
export GIT_EMSCRIPTEN=https://github.com/kripken/emscripten.git
export GIT_EMSCRIPTEN_FASTCOMP=https://github.com/kripken/emscripten-fastcomp
export GIT_EMSCRIPTEN_FASTCOMP_CLANG=https://github.com/kripken/emscripten-fastcomp-clang
export EMCC_CORES=$CORES
export EMSCRIPTEN_VERSION=1.20.0

# gtest relies on cxxabi, so we need to include this following hack
export CFLAGS="-O3"
export CPPFLAGS="-O3"
export CXXFLAGS="-O3 -I$INSTALL_DIR/include -I$BUILD_DIR/emscripten/system/lib/libcxxabi/include"
export LDFLAGS="-O3 -L$INSTALL_DIR/lib"

mkdir -p $BUILD_DIR
mkdir -p $INSTALL_DIR
