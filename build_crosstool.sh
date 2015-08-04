#!/bin/bash

# Take input from /dev/null.
exec < /dev/null

# stop on any error, echo commands.
set -ex

# Set locale to C, so that e.g., 'sort' will work consistently regardless
# of system and user environment settings.
LC_ALL=C
export LC_ALL

absname=`readlink -f "$0"`
absroot="${absname%/*}"

[ -f "${absroot}/grte/grte.cfg" ] || {
  error "could not find ${absroot}/grte/grte.cfg"
}

. "${absroot}/grte/grte.cfg"

GRTEROOT="${1}/v${GRTEVERSION}"
tb=`readlink -f "${2}"`
GRTEBASENAME="${GRTE_PACKAGE_PREFIX}$(basename $1)v${GRTEVERSION}"
STAGING="${tb}/staging"
RESULTS="${tb}/results"
DEB_DIR=${RESULTS}/debs

# Directory that stores upstream sources
CROSSTOOL_SOURCES=$3

# Crosstool configuration
CROSSTOOL_VERSION="v5"

CROSSTOOL_GCC_VERSION="4.9"

# Assume the clang source code is checked out following
# http://clang.llvm.org/get_started.html
CROSSTOOL_CLANG_VERSION="3.7"

: ${crosstool_rpmver:="1.0"}
# Update this each time new RPM's are built.
: ${crosstool_rpmrel:="8"}

export PARALLELMFLAGS="${JFLAGS:-j8}"
[ -z "${EMAIL}" ] && {
    EMAIL="foo@bar.io"
    export EMAIL
}

# Install the packages for GRTE, mostly GDE
for pkg in runtime headers gde; do
    dpkg -i ${DEB_DIR}/${GRTEBASENAME}-${pkg}_${grte_rpmver}-${grte_rpmrel}_amd64.deb
done

# Use bash as shell, other "source" command inside rpm spec will fail.
ln -sf /bin/bash /bin/sh

# install packages that are needed by building binutils and clang
apt-get update
apt-get install -y flex bison rpm texinfo texi2html libxml2-dev make alien

function build_rpm() {
    local rpmrel=$1
    local spec_file=$2
    rpmbuild \
        --dbpath /dev/null \
        --define "_hash_empty_files 1" \
        --define "_sourcedir ${CROSSTOOL_SOURCES}" \
        --define "_topdir ${STAGING}" \
        --define "_rpmtopdir ${STAGING}" \
        --define 'disable_debuginfo t' \
        --define "maintainer_email ${EMAIL}" \
	--define "grte_basename ${GRTEBASENAME}" \
	--define "grte_root ${GRTEROOT}" \
	--define "grte_version ${GRTEVERSION}" \
	--define "grte_gcc_version ${gcc_version}" \
	--define "grte_glibc_version ${glibc_version}" \
	--define "grte_rpmver ${grte_rpmver}" \
	--define "grte_rpmrel ${grte_rpmrel}" \
        --define "crosstool_scripts ${absroot}/crosstool/scripts" \
        --define "crosstool_version ${CROSSTOOL_VERSION}" \
        --define "crosstool_rpmver ${crosstool_rpmver}" \
        --define "crosstool_rpmrel ${rpmrel}" \
        --define "crosstool_gcc_version ${CROSSTOOL_GCC_VERSION}" \
        --define "gcc_svn_version ${GCC_SVN_VERSION}" \
        --define "crosstool_clang_version ${CROSSTOOL_CLANG_VERSION}" \
        --define "clang_svn_version ${CLANG_SVN_VERSION}" \
        -bb ${spec_file}
}

function package() {
    local name=$1  # gcc, clang
    local version=$2  # gcc version, or clang version
    local svn_version=$3
    local rpm_rel=${crosstool_rpmrel}.${svn_version}svn
    build_rpm ${rpm_rel} crosstool/crosstool-grte-${name}.spec
    local package_prefix="${GRTEBASENAME}-crosstool${CROSSTOOL_VERSION}-${name}-${version}"
    local rpm="RPMS/x86_64/${package_prefix}-${crosstool_rpmver}-${rpm_rel}.x86_64.rpm"
    pushd $STAGING
    ${absroot}/crosstool/scripts/rpm_to_deb "$rpm"
    mv "${package_prefix}_${crosstool_rpmver}-${rpm_rel}_amd64.deb" \
	"${package_prefix}_${crosstool_rpmver}-${rpm_rel}_amd64.changes" \
	"${RESULTS}/debs/"
    mv "$rpm" "${RESULTS}/rpms/"
    popd
}

set -e
# For test rpm creation and deb conversion.
# package foo ${CROSSTOOL_GCC_VERSION} ${GCC_SVN_VERSION}

[ -z "${SKIP_CROSSTOOL_GCC}" ] && {
    package gcc ${CROSSTOOL_GCC_VERSION} ${GCC_SVN_VERSION}
}

# Install the crosstool gcc to build clang
dpkg -i ${DEB_DIR}/${GRTEBASENAME}-crosstool${CROSSTOOL_VERSION}-gcc-${CROSSTOOL_GCC_VERSION}_${crosstool_rpmver}-${crosstool_rpmrel}.${GCC_SVN_VERSION}svn_amd64.deb

# Build cmake because cmake in ubuntu 13 is too old
mkdir -p ${STAGING}/cmake
tar zxf ${CROSSTOOL_SOURCES}/cmake-3.2.3.tar.gz -C ${STAGING}/cmake
pushd ${STAGING}/cmake/cmake-3.2.3
./configure --parallel=${PARALLELMFLAGS}
make ${PARALLELMFLAGS}
make install
popd

package clang ${CROSSTOOL_CLANG_VERSION} ${CLANG_SVN_VERSION}
