%define gcc_glibc_version gcc-4.4.0-glibc-2.3.6-grte
%define base_summary %{gcc_glibc_version} compiler
Summary: %{base_summary}
Name: crosstool%{crosstool_version}-%{gcc_glibc_version}
Version: 1.0
Release: 36185
License: GPL/LGPL
Group: Development/Languages
Packager: C Compiler Team <c-compiler-team@google.com>

Source0: crosstool-scripts.tar.gz
Source1: gcc-4.4.0_gg.tar.bz2
Source2: binutils-2.19.1_gg.tar.bz2
Source3: gold-20090815.tar.bz2
Source4: gmp-4.2.4.tar.bz2
Source5: mpfr-2.4.1.tar.bz2
Source6: ppl-0.10.tar.bz2
Source7: cloog-ppl-0.15.tar.gz
Source8: mao-604.tar.bz2

Patch0: gold-20090818-hidden.patch
Patch1: gold-20090819-debug_msg-test.patch
Patch2: gold-20090824-dash-s.patch
Patch3: gold-20090904-output-perm.patch
Patch4: gold-20091010-searched-file.patch

BuildRoot: %{_tmppath}/%{name}-buildroot

# Create debuginfo unless disable_debuginfo is defined.
%define make_debuginfo %{?disable_debuginfo:""}%{!?disable_debuginfo:"t"}

# Remove BuildRoot in %clean unless keep_buildroot is defined.
%define remove_buildroot %{?keep_buildroot:""}%{!?keep_buildroot:"t"}

# Enable bootstrapping unless disable_bootstrap is defined.
%define bootstrap_config_arg %{?disable_bootstrap:"--disable-bootstrap"}%{!?disable_bootstrap:""}

%description
This SRPM builds Google's %{gcc_glibc_version} compilers.

%prep
%setup -c
%setup -T -D -a 1
%setup -T -D -a 2
%setup -T -D -a 3
%setup -T -D -a 4
%setup -T -D -a 5
%setup -T -D -a 6
%setup -T -D -a 7
%setup -T -D -a 8

cd gcc-4.4.0
# Fix timestamps of extracted sources.
contrib/gcc_update --touch
cd ..

cd gold
chmod -R u+w .  # Make sure extracted sources are writable.
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
cd ..

%define crosstool_top /usr/crosstool/%{crosstool_version}
%define target_top %{crosstool_top}/%{gcc_glibc_version}
%define grte_top /usr/grte/v1

%build
BUGURL=http://wiki.corp.google.com/Main/CrosstoolV13Issues
PKGVERSION=Google_%{name}-%{version}-%{release}
# For an actual release build, which doesn't have any special text in the
# Release field, we do not include the version number.  This is done so
# that binaries will rebuild identically (if their sources aren't changed)
# in subsequent rebuilds.  (We don't use if/else so that this is more
# diffable with other crosstool specs, which always include versions.)
if echo %{release} | grep '^[0-9][0-9]*$' > /dev/null; then
  PKGVERSION=Google_%{name}
fi

source scripts/crosstool.sh

export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"

WORK_DIR="$RPM_BUILD_DIR/$RPM_PACKAGE_NAME-$RPM_PACKAGE_VERSION"
BINUTILS_SRC_SUBDIR="binutils-2.19.1"
GCC_SRC_SUBDIR="gcc-4.4.0"
GOLD_SRC_SUBDIR="gold"
GMP_SRC_SUBDIR="gmp-4.2.4"
MPFR_SRC_SUBDIR="mpfr-2.4.1"
PPL_SRC_SUBDIR="ppl-0.10"
CLOOGPPL_SRC_SUBDIR="cloog-ppl"
MAO_SRC_SUBDIR="mao"

CC_COMMON="%{grte_top}/bin/gcc -m64"
CXX_COMMON="%{grte_top}/bin/g++ -m64"
COMMON_GCC_OPTIONS=" \
    --enable-shared=libgcc,libmudflap,libssp,libstdc++,libgfortran \
    --with-pic=libgfortran \
    --enable-languages=c,c++,fortran --with-sysroot=%{grte_top} \
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

# Would be nice to build these only once (since they're target-independent),
# but currently the debug sources are packaged per-target.

# We install gmp since its headers are used by gcc plugins
build_hostlib "$WORK_DIR/$GMP_SRC_SUBDIR" "$WORK_DIR/build-gmp" \
              "$PREFIX" --enable-cxx

build_hostlib "$WORK_DIR/$MPFR_SRC_SUBDIR" "$WORK_DIR/build-mpfr" \
              "$HOSTLIB_PREFIX" --with-gmp="$PREFIX"
build_hostlib "$WORK_DIR/$PPL_SRC_SUBDIR" "$WORK_DIR/build-ppl" \
              "$HOSTLIB_PREFIX" --with-libgmp-prefix="$PREFIX" \
              --with-cxxflags=-frandom-seed=\$@
build_hostlib "$WORK_DIR/$CLOOGPPL_SRC_SUBDIR" "$WORK_DIR/build-cloog-ppl" \
              "$HOSTLIB_PREFIX" --with-gmp="$PREFIX" \
              --with-ppl="$HOSTLIB_PREFIX"

build_binutils "$WORK_DIR/$BINUTILS_SRC_SUBDIR" "$WORK_DIR/build-binutils" \
               "$PREFIX" "$TARGET" --with-sysroot=%{grte_top} \
               --with-bugurl="$BUGURL" --with-pkgversion="$PKGVERSION" \
               --enable-targets=i686-unknown-linux-gnu

# --with-host-libstdcxx setting is needed to link if using PPL.
build_gcc "$WORK_DIR/$GCC_SRC_SUBDIR" "$WORK_DIR/build-gcc" \
          "$PREFIX" "$TARGET" \
          --enable-multilib \
          --enable-targets=all \
          --with-arch-32=pentium3 \
          --with-tune-32=pentium4 \
          $debug_map_config_arg \
          %{bootstrap_config_arg} \
          $COMMON_GCC_OPTIONS \
          --with-gmp="$PREFIX" \
          --with-mpfr="$HOSTLIB_PREFIX" \
          --with-ppl="$HOSTLIB_PREFIX" \
          --with-cloog="$HOSTLIB_PREFIX" \
          --with-host-libstdcxx="-lstdc++" \
          FCFLAGS="-g -O2 $debug_map_build_arg" \
          AR_FOR_TARGET="$WORK_DIR/dar" \
          RANLIB_FOR_TARGET="$WORK_DIR/dranlib"
archive_ld "$PREFIX" "$TARGET"
build_gold "$WORK_DIR/$GOLD_SRC_SUBDIR" "$WORK_DIR/build-gold" \
           "$PREFIX" "$TARGET" \
           --with-sysroot=%{grte_top} --enable-targets=i686-unknown-linux-gnu \
           --with-bugurl="$BUGURL" --with-pkgversion="$PKGVERSION"
build_mao "$WORK_DIR/$MAO_SRC_SUBDIR" "$WORK_DIR/build-mao" \
          "$PREFIX" "$TARGET" \
          "$WORK_DIR/$BINUTILS_SRC_SUBDIR" \
          "$WORK_DIR/build-binutils"
wrap_gas_with_mao "$WORK_DIR/$MAO_SRC_SUBDIR" "$PREFIX" "$TARGET"

make_traditional_crosstool_layout "$RPM_BUILD_ROOT" "%{crosstool_top}" \
                                  "%{gcc_glibc_version}"

# Now we hack things a bit to support Fortran.  For Crosstool v13 GA, we
# released the compiler with a shared libgfortran but did not install
# libgfortran.so in production.  The result: http://b/2160690.  We need to
# continue to support any binaries which may have been compiled with the GA
# compilers, so libgfortran.so must continue to live in the runtimes package,
# but we're moving to a static libgfortran compiled with -fPIC for code
# compiled with newer compilers.  We move the shared libgfortran to a new
# location (in the devel package only) so it won't get picked up by default but
# can be used if needs be.
for lib_base in lib lib64; do
  lib_prefix="$RPM_BUILD_ROOT/%{target_top}/x86/$lib_base"
  libgfortran_prefix="$lib_prefix/libgfortran"

  mkdir "$libgfortran_prefix"
  mv "$lib_prefix/libgfortran.so"* "$libgfortran_prefix"
done

if [ -n "%{make_debuginfo}" ]; then
  # Copy sources into the build area.  First we copy the source directories,
  # then we copy any files that look like generated or symlinked sources in
  # the build directories.
  mkdir -p "$DBGSRC_PREFIX"
  copy_debug_sources "$WORK_DIR/$BINUTILS_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$BINUTILS_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$GCC_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$GCC_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$GOLD_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$GOLD_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$GMP_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$GMP_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$MPFR_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$MPFR_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$PPL_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$PPL_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$CLOOGPPL_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$CLOOGPPL_SRC_SUBDIR"
  copy_debug_sources "$WORK_DIR/$MAO_SRC_SUBDIR" \
                     "$DBGSRC_PREFIX/$MAO_SRC_SUBDIR"
  # Need certain directories because they're traversed in debug file name
  # specs.  Need symlinks copied as files because they point to absolute
  # paths.
  debugsrc_build_dirs="
    build-binutils
    build-cloog
    build-gcc
    build-gmp
    build-gold
    build-mpfr
    build-ppl
    hostlibs
  "
  (cd $WORK_DIR && \
    find $debugsrc_build_dirs \
    \( -type d -name .libs \) -prune -o \
    \( -name "*.so" \) -prune -o \
    \( -type f -name "*.c" \) -print -o \
    \( -type f -name "*.h" \) -print -o \
    \( -type f -name "*.cc" \) -print -o \
    \( -type f -name "*.tcc" \) -print -o \
    \( -type f -name "*.inc" \) -print -o \
    \( -type f -iname "*.s" \) -print -o \
    \( -type d -name gcc \) -print -o \
    \( -type d -name libgcc \) -print -o \
    -type l -print | \
    cpio -pdL "$DBGSRC_PREFIX")
  # Make sure that the debug sources are read-write by root and readable
  # by all users.  (Sets x bits for all directories, and makes x bits
  # for files consistent for user,group,other.)
  chmod -R u=rwX,go=rX "$DBGSRC_PREFIX"

  strip_libs_and_make_debuginfo "$PREFIX" "$PREFIX"
  strip_libs_and_make_debuginfo "$PREFIX" "$RUNTIME_PREFIX_32"
  strip_libs_and_make_debuginfo "$PREFIX" "$RUNTIME_PREFIX_64"
  strip_exes_and_make_debuginfo "$PREFIX" "$PREFIX"
fi

create_file_lists "$RPM_BUILD_ROOT" "%{target_top}" \
                  "$RUNTIME_TOP_32" "$RUNTIME_TOP_64"


%install
# Set PATH here so the scripts run by __spec_install_post, which use
# 'strip' from PATH, use the GRTE 'strip'.
export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"

%clean
if [ -n "%{remove_buildroot}" ]; then
  rm -rf %{buildroot}
fi
# Remove the top-level RPM, since it's empty.
rm -f %{_rpmdir}/%{_target_cpu}/%{name}-%{version}-%{release}.%{_target_cpu}.rpm

%files

# devel package
%package devel
Summary: %{base_summary} for x86_64 and i686
Group: Development/Languages
Requires: grte-runtimes grte-headers

%description devel
%{summary}

%files devel -f files.devel

# runtimes package
%package runtimes
Summary: %{base_summary} runtimes for x86_64 and i686
Group: Development/Languages
Requires: grte-runtimes

%description runtimes
%{summary}

%files runtimes -f files.runtimes

# debuginfo package
%if %{make_debuginfo}
%package debuginfo
Summary: %{base_summary} debuginfo for x86_64 and i686
Group: Development/Languages

%description debuginfo
%{summary}

%files debuginfo -f files.debuginfo
%endif

%changelog
* Sun Nov 01 2009 Ollie Wild <aaw@google.com>
- For bug http://b/2222512 ...
  Integrates CL 36173 (rollback of CL 34946).

* Sat Oct 17 2009 Chris Demetriou <cgd@google.com>
- Bump version number to 1.0.  (Integrates all changes from trunk @35850.)

* Sat Sep 12 2009 Chris Demetriou <cgd@google.com>
- Bump version number to 0.2.  (Integrates all changes from trunk @34569.)

* Fri Aug 07 2009 Chris Demetriou <cgd@google.com>
- Bump version number to 0.1-2 for a build.  (Integrates all
  changes from trunk.)

* Mon Aug 03 2009 Chris Demetriou <cgd@google.com>
- Created Crosstool V13 release branch.  Bump version number to
  0.1-1 for a build.
