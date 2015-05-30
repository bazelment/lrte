#!/bin/bash

absname=`readlink -f "$0"`
absroot="${absname%/*}"

[ -f "${absroot}/../grte.cfg" ] || {
  error "could not find ${absroot}/../grte.cfg"
}

. "${absroot}/../grte.cfg"

wget https://ftp.gnu.org/gnu/glibc/glibc-${glibc_version}.tar.bz2
wget http://ftp.gnu.org/gnu/binutils/binutils-${binutils_version}.tar.bz2
wget https://ftp.gnu.org/gnu/gcc/gcc-${gcc_version}/gcc-${gcc_version}.tar.bz2
wget https://ftp.gnu.org/gnu/gmp/gmp-${gmp_version}.tar.bz2
wget https://ftp.gnu.org/gnu/mpfr/mpfr-${mpfr_version}.tar.bz2
wget https://ftp.gnu.org/gnu/mpc/mpc-${mpc_version}.tar.gz
wget http://zlib.net/zlib-${zlib_version}.tar.gz
wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-${headers26}.tar.xz

