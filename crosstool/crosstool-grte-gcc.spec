%define gcc_glibc_version gcc-%{grte_gcc_version}-%{grte_basename}
%define base_summary %{gcc_glibc_version} compiler for %{GRTEROOT}
Summary: %{base_summary}
Name: %{grte_basename}-crosstool%{crosstool_version}-gcc-%{crosstool_gcc_version}
Version: 1.0
Release: 8
License: GPL/LGPL
Group: Development/Languages
Packager: Release Engineer <%{maintainer_email}>
AutoReqProv: no
Requires: %{grte_basename}-runtime %{grte_basename}-headers

# Source0: crosstool-scripts.tar.gz
Source0: binutils-2.25.tar.bz2
Source1: gmp-6.0.0a.tar.bz2
Source2: mpc-1.0.3.tar.gz
Source3: mpfr-3.1.2.tar.bz2
# Patch0: binutils-2.24-set-section-macros.patch

BuildRoot: %{_tmppath}/%{name}-buildroot

# Create debuginfo unless disable_debuginfo is defined.
%define make_debuginfo %{?disable_debuginfo:""}%{!?disable_debuginfo:"t"}
%define debug_cflags %{?disable_debuginfo:""}%{!?disable_debuginfo:"-g"}

# Remove BuildRoot in %clean unless keep_buildroot is defined.
%define remove_buildroot %{?keep_buildroot:""}%{!?keep_buildroot:"t"}

# Enable bootstrapping unless disable_bootstrap is defined.
%define bootstrap_config_arg %{?disable_bootstrap:"--disable-bootstrap"}%{!?disable_bootstrap:""}

%description
GCC %{crosstool_gcc_version} to work with %{grte_basename}

%prep
%setup -c
%setup -T -D -a 0
%setup -T -D -a 1
%setup -T -D -a 2
%setup -T -D -a 3

# cd binutils-2.25
# %patch0 -p0
# cd ..

%define crosstool_top /usr/crosstool/%{crosstool_version}
%define target_top %{crosstool_top}/%{gcc_glibc_version}
%define grte_top %{grte_root}

%build
BUGURL=http://www.github.com/crosstool/bug
PKGVERSION=CROSSTOOL_%{name}-%{version}-%{release}
# For an actual release build, which doesn't have any special text in the
# Release field, we do not include the version number.  This is done so
# that binaries will rebuild identically (if their sources aren't changed)
# in subsequent rebuilds.  (We don't use if/else so that this is more
# diffable with other crosstool specs, which always include versions.)
if echo %{release} | grep '^[0-9][0-9]*$' > /dev/null; then
  PKGVERSION=CROSSTOOL_%{name}
fi

source %{crosstool_scripts}/crosstool.sh

export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"

WORK_DIR="$RPM_BUILD_DIR/$RPM_PACKAGE_NAME-$RPM_PACKAGE_VERSION"

BINUTILS_SRC_SUBDIR="binutils-2.25"
GCC_SRC_SUBDIR="gcc-%{crosstool_gcc_version}"

CFLAGS="-O2 -isystem %{grte_top}/include -L%{grte_top}/lib64"
CC_COMMON="%{grte_top}/bin/gcc -m64 ${CFLAGS}"
CXX_COMMON="%{grte_top}/bin/g++ -m64 ${CFLAGS}"
LDFLAGS="-Wl,-I,%{grte_top}/lib64/ld-linux-x86-64.so.2"
COMMON_GCC_OPTIONS=" \
    --enable-shared=libgcc,libssp,libstdc++\
    --enable-languages=c,c++ --with-sysroot=%{grte_top} \
    --with-runtime-root-prefix=%{grte_top} \
    --with-native-system-header-dir=/include \
    --with-local-prefix=/ \
    --with-bugurl=$BUGURL --with-pkgversion=$PKGVERSION \
    --enable-clocale=gnu \
    --enable-linker-build-id \
    "

# We build for x86_64 and bootstrap a compiler that supports i686 multilibs.
TARGET=x86_64-unknown-linux-gnu
PREFIX="$RPM_BUILD_ROOT%{target_top}/x86"
DBGSRC_TOP="%{target_top}/x86/debug-src"
DBGSRC_PREFIX="$RPM_BUILD_ROOT$DBGSRC_TOP"
RUNTIME_TOP_32="%{crosstool_top}/i686-unknown-linux-gnu"
RUNTIME_TOP_64="%{crosstool_top}/x86_64-unknown-linux-gnu"
RUNTIME_PREFIX_32="$RPM_BUILD_ROOT$RUNTIME_TOP_32/lib"
RUNTIME_PREFIX_64="$RPM_BUILD_ROOT$RUNTIME_TOP_64/lib64"
HOSTLIB_PREFIX="$WORK_DIR/hostlibs"
debug_map_build_arg=
debug_map_config_arg=
if [ -n "%{make_debuginfo}" ]; then
  debug_map_build_arg="-fdebug-prefix-map=$WORK_DIR=$DBGSRC_TOP"
  debug_map_config_arg="--with-debug-prefix-map=$WORK_DIR=$DBGSRC_TOP"
fi
export CC="$CC_COMMON $debug_map_build_arg"
export CXX="$CXX_COMMON $debug_map_build_arg"

# Create deterministic-mode wrappers around GRTE ar and ranlib for builds
# of host libraries.
make_deterministic_ar_wrapper "%{grte_top}" "$WORK_DIR/dar"
make_deterministic_ranlib_wrapper "%{grte_top}" "$WORK_DIR/dranlib"
export "AR=$WORK_DIR/dar"
export "RANLIB=$WORK_DIR/dranlib"

rm -rf $RPM_BUILD_ROOT

build_binutils "$WORK_DIR/$BINUTILS_SRC_SUBDIR" "$WORK_DIR/build-binutils" \
               "$PREFIX" "$TARGET" --with-sysroot=%{grte_top} \
               --with-bugurl="$BUGURL" --with-pkgversion="$PKGVERSION" \
               --enable-gold

export PATH="${PREFIX}/bin:${PREFIX}/sbin:$PATH"
# Checked out into upstream/ from svn://gcc.gnu.org/svn/gcc/branches/google/gcc-4_9
cp -r %{_sourcedir}/gcc-4_9 $WORK_DIR/gcc-src
mv $WORK_DIR/gmp-6.0.0 $WORK_DIR/gcc-src/gmp
mv $WORK_DIR/mpc-1.0.3 $WORK_DIR/gcc-src/mpc
mv $WORK_DIR/mpfr-3.1.2 $WORK_DIR/gcc-src/mpfr

mkdir $WORK_DIR/build-gcc
cd $WORK_DIR/build-gcc
CC=$CC \
CXX=$CXX \
CFLAGS=$CFLAGS \
CXXFLAGS=$CFLAGS \
LDFLAGS=$LDFLAGS \
LD_FOR_TARGET=${PREFIX}/bin/ld \
$WORK_DIR/gcc-src/configure \
    --disable-nls --enable-threads=posix \
    --enable-symvers=gnu --enable-__cxa_atexit \
    --enable-c99 --enable-long-long \
    --with-gnu-as --with-gnu-ld \
    --prefix="%{target_top}/x86" \
    --host="${TARGET}" \
    --build="${TARGET}" \
    --target="${TARGET}" \
    --disable-multilib \
    --with-multilib-list=m64 \
    --enable-targets=all \
    $debug_map_config_arg \
    %{bootstrap_config_arg} \
    $COMMON_GCC_OPTIONS \
    --with-host-libstdcxx="-lstdc++" \
    AR_FOR_TARGET="$WORK_DIR/dar" \
    RANLIB_FOR_TARGET="$WORK_DIR/dranlib"
make $PARALLELMFLAGS FCFLAGS="%{debug_cflags} -O2 $debug_map_build_arg"
make install DESTDIR=$RPM_BUILD_ROOT

# Would be nice to build these only once (since they're target-independent),
# but currently the debug sources are packaged per-target.
mkdir $WORK_DIR/rebuild-binutils
cd $WORK_DIR/rebuild-binutils
CC=$CC \
CXX=$CXX \
CFLAGS=$CFLAGS \
CXXFLAGS=$CFLAGS \
LDFLAGS=$LDFLAGS \
$WORK_DIR/$BINUTILS_SRC_SUBDIR/configure \
    --prefix="%{target_top}/x86" \
    --host="${TARGET}" \
    --build="${TARGET}" \
    --target="${TARGET}" \
    --disable-nls \
    --enable-gold \
    --enable-shared \
    --enable-64-bit-bfd \
    --with-sysroot=%{grte_top} \
    --with-native-lib-dirs=%{grte_top}/lib \
    --with-bugurl="$BUGURL" \
    --with-pkgversion="$PKGVERSION" \
    --enable-gold \
    --enable-plugins
make $PARALLELMFLAGS
make install DESTDIR=$RPM_BUILD_ROOT

# Make gold the default linker
rm -f ${PREFIX}/bin/ld
ln -s ld.gold ${PREFIX}/bin/ld

%install
# Set PATH here so the scripts run by __spec_install_post, which use
# 'strip' from PATH, use the GRTE 'strip'.
export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"

%clean
# if [ -n "%{remove_buildroot}" ]; then
#   rm -rf %{buildroot}
# fi
#
# rm -f %{_rpmdir}/%{_target_cpu}/%{name}-%{version}-%{release}.%{_target_cpu}.rpm

%files

%defattr(-,root,root)
%{target_top}/x86/*

%changelog
* Thu Jun 01 2015 Ming Zhao <mzhao@luminatewireless.com>
- Build gcc 4.9.2 and binutils 2.25.
