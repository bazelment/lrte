#!/bin/bash

# Check the LRTE runtime and Crosstool can be used.

absname=`readlink -f "$0"`
absroot="${absname%/*}"

. "${absroot}/grte/grte.cfg"

GRTEROOT="${1}/v${GRTEVERSION}"
tb=`readlink -f "${2}"`
GRTEBASENAME="${GRTE_PACKAGE_PREFIX}$(basename $1)v${GRTEVERSION}"
STAGING="${tb}/staging"
RESULTS="${tb}/results"
DEB_DIR=${RESULTS}/debs

# Install the packages for GRTE
for pkg in runtime headers; do
    dpkg -i ${DEB_DIR}/${GRTEBASENAME}-${pkg}_${grte_rpmver}-${grte_rpmrel}_amd64.deb
done

dpkg -i ${DEB_DIR}/${GRTEBASENAME}-crosstoolv2-*_amd64.deb

export CROSSTOOL_TOP=/usr/crosstool/v2/gcc-${gcc_version}-${GRTEBASENAME}/x86/bin/
# Put llvm-symbolizer to the path
export PATH=${CROSSTOOL_TOP}:$PATH

# Check normal build
${CROSSTOOL_TOP}/clang++ hello.cc -o /tmp/hello
/tmp/hello

# Check address sanitizer build
${CROSSTOOL_TOP}/clang++ -fsanitize=address hello.cc -o /tmp/hello
/tmp/hello


