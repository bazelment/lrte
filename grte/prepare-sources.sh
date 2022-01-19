#!/bin/bash

exec < /dev/null

# stop on any error, echo commands.
set -ex

# Set locale to C, so that e.g., 'sort' will work consistently regardless
# of system and user environment settings.
LC_ALL=C
export LC_ALL

# The 'gzip' environment variable passes flags to gzip.  We set -n to
# avoid putting timestamps and filenames in gzip files.  This enables
# deterministic builds.
GZIP=-n
export GZIP

absname=`readlink -f "$0"`
absroot="${absname%/*}"

[ -f "${absroot}/grte.cfg" ] || {
  error "could not find ${absroot}/grte.cfg"
}

. "${absroot}/grte.cfg"

OSRC="${absroot}/sources"
TAR_DIR=`readlink -f ${TAR_DIR:-/sources}`

echo "Unpack sources to ${OSRC}"
mkdir -p "${OSRC}"
cd "${OSRC}"

tar zxf ${TAR_DIR}/zlib-${zlib_version}.tar.gz
tar Jxf ${TAR_DIR}/gcc-${gcc_version}.tar.xz
tar jxf ${TAR_DIR}/gmp-${gmp_version}.tar.bz2
tar jxf ${TAR_DIR}/mpfr-${mpfr_version}.tar.bz2
tar zxf ${TAR_DIR}/mpc-${mpc_version}.tar.gz
mv gmp-${gmp_version} gcc-${gcc_version}/gmp
mv mpfr-${mpfr_version} gcc-${gcc_version}/mpfr
mv mpc-${mpc_version} gcc-${gcc_version}/mpc
cp gcc-${gcc_version}/gcc/Makefile.in gcc-Makefile.in.orig
tar Jxf ${TAR_DIR}/linux-${headers26}.tar.xz
make -C linux-${headers26} headers_install \
    INSTALL_HDR_PATH=${OSRC}/linux-libc-headers-${headers26} \
    ARCH=x86
tar jxf ${TAR_DIR}/binutils-${binutils_version}.tar.bz2
cd binutils-${binutils_version}
# patch -p0 < ${TAR_DIR}/binutils-2.24-set-section-macros.patch
find . -iname *.info -exec touch {} \;
find . -iname *.po -exec touch {} \;
cd "${OSRC}"
tar jxf ${TAR_DIR}/glibc-${glibc_version}.tar.bz2
