#!/usr/bin/env bash

export VAGRANT_DIR=/vagrant

cd $VAGRANT_DIR && source ./set_env.sh
cd $VAGRANT_DIR && source ./install_prereqs.sh
cd $VAGRANT_DIR && source ./install_emscripten.sh
cd $VAGRANT_DIR && source ./build_regex2dfa.sh
