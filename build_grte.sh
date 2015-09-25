#!/bin/bash

# This runs inside docker container as root to build GRTE

set -ex
apt-get update
# Make sure requires packages are installed(either on host or insider
# docker)
apt-get install -y texinfo texi2html xz-utils make gcc g++

GRTE_PREFIX=$1
GRTE_TMPDIR=$2
mkdir ${GRTE_PREFIX}

rm -rf grte/sources/*
./grte/prepare-sources.sh
./grte/grte-build ${GRTE_PREFIX} ${GRTE_TMPDIR}
./grte/grte-package ${GRTE_PREFIX} ${GRTE_TMPDIR}
