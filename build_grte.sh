#!/bin/bash

# This runs inside docker container as root to build GRTE

set -ex
apt-get update
apt-get install -y texinfo texi2html xz-utils

GRTE_PREFIX=$1
GRTE_TMPDIR=$2
mkdir ${GRTE_PREFIX}

rm -rf grte/sources/*
./grte/prepare-sources.sh
./grte/grte-build ${GRTE_PREFIX} ${GRTE_TMPDIR}
./grte/grte-package ${GRTE_PREFIX} ${GRTE_TMPDIR}
