#!/bin/bash

# Download gcc code from svn.
SVN_TOP=${SVN_TOP:-upstream}
BRANCH=branches/google/gcc-4_9
cd ${SVN_TOP}
svn co svn://gcc.gnu.org/svn/gcc/${BRANCH}
