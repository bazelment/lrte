#!/bin/bash

# This runs inside docker container as root to build GRTE

set -ex
apt-get update
# Make sure requires packages are installed(either on host or insider
# docker)
# xz-utils: needed to unpack kernel source
# gawk: used by building glibc
# rpm: rpmbuild to build rpm package
# alien, fakeroot, debhelper: convert rpm package to debian package
# python: 2to3
apt-get install -y texinfo texi2html xz-utils make gcc g++ gawk \
	rpm alien fakeroot debhelper python

apt-get install -y python3 bison libisl-dev libgmp-dev  libmpc-dev libmpfr-dev

GRTE_PREFIX=$1
GRTE_TMPDIR=$2
mkdir ${GRTE_PREFIX}

rm -rf grte/sources/*
./grte/prepare-sources.sh
./grte/grte-build ${GRTE_PREFIX} ${GRTE_TMPDIR}
./grte/grte-package ${GRTE_PREFIX} ${GRTE_TMPDIR}
