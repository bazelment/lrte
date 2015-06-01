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
GRTEBASENAME="${GRTE_PACKAGE_PREFIX}$(basename $1)v${GRTEVERSION}"
DEB_DIR=$2
CROSSTOOL_SOURCES=$3

# Crosstool configuration
CROSSTOOL_VERSION="v2"
CROSSTOOL_GCC_VERSION="4.9.2"
CROSSTOOL_CLANG_VERSION="3.6"
# Directory that stores upstream sources

export PARALLELMFLAGS="${JFLAGS:-j8}"
[ -z "${EMAIL}" ] && {
    EMAIL="foo@bar.io"
    export EMAIL
}

Install the packages for GRTE, mostly GDE
for pkg in runtime headers gde; do
    dpkg -i ${DEB_DIR}/${GRTEBASENAME}-${pkg}_${grte_rpmver}-${grte_rpmrel}_amd64.deb
done
bash

# Use bash as shell, other "source" command inside rpm spec will fail.
ln -sf /bin/bash /bin/sh

apt-get update
# install packages that are needed by building binutils
apt-get install -y flex bison rpm texinfo texi2html

STAGING=/tmp/rpmbuild

function build_rpm() {
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
        --define "crosstool_gcc_version ${CROSSTOOL_GCC_VERSION}" \
        --define "crosstool_clang_version ${CROSSTOOL_CLANG_VERSION}" \
        -bb $@
}

build_rpm crosstool/crosstool-grte-gcc.spec
crosstool/scripts/rpm_to_deb \
$STAGING/RPMS/x86_64/${GRTEBASENAME}-crosstool${CROSSTOOL_VERSION}-gcc-${CROSSTOOL_GCC_VERSION}-1.0-8.x86_64.rpm
