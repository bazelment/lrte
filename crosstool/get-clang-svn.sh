#!/bin/bash -e

# Get clang's source code from svn
SVN_TOP=${SVN_TOP:-upstream}
BRANCH=branches/google/stable
cd ${SVN_TOP}
svn co http://llvm.org/svn/llvm-project/llvm/${BRANCH} llvm
svn co http://llvm.org/svn/llvm-project/compiler-rt/${BRANCH} llvm/projects/compiler-rt
svn co http://llvm.org/svn/llvm-project/cfe/${BRANCH} llvm/tools/clang
svn co http://llvm.org/svn/llvm-project/clang-tools-extra/${BRANCH} llvm/tools/clang/tools/extra
