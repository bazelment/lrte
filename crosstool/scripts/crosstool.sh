#
# crosstool.sh
# Build a GNU/Linux toolchain
#
# Copyright (c) 2001 by Bill Gatliff, bgat@billgatliff.com 
# Copyright (c) 2003 by Dan Kegel, Ixia Communications, 
# Copyright (c) 2004,2005 by Dan Kegel, Google, Inc.
# Copyright (c) 2008 by Ollie Wild, Google, Inc.
# All rights reserved.  This script is provided under the terms of the GPL.

# We build native x86_64 compilers with host = build = target to make sure gcc
# bootstraps and all tools have a consistent naming
readonly DEFAULT_HOST=x86_64-unknown-linux-gnu

#
# Usage: abort MESSAGE...
#
# Print a line including MESSAGE... and exit with a non-zero exit status.
#
abort() {
    echo "${FUNCNAME[1]}: $@" 1>&2
    exit 1
}

#
# Usage: logresult STAGE REPRESENTATIVE_FILE
#
# Aborts the build if REPRESENTATIVE_FILE does not exist or is not executable.
# Used to log success or failure of each stage.
#
logresult() {
    if test -x $2; then
        echo crosstool: $1 built ok
    else
        abort "Build failed during $1"
    fi
}

#
# Usage: pushd DIR
#
# Add DIR to the top of the directory stack and make it the current working
# directory.
#
push_dir() {
  [ $# -eq 1 ] || abort "incorrect call syntax"
  pushd "$1" > /dev/null
}

#
# Usage: pop_dir
#
# Pop the top entry of the directory stack and make the new top the current
# working directory.
#
pop_dir() {
  [ $# -eq 0 ] || abort "incorrect call syntax"
  popd > /dev/null
}

#
# Usage: make_distcc_masquerade_dir BUILD_PREFIX
#
# Make distcc masquerade directory for the toolchain currently installed at
# prefix BUILD_PREFIX.
#
make_distcc_masquerade_dir() {
  [ $# -eq 1 ] || abort "incorrect call syntax"

  local build_prefix
  build_prefix="$1"

  push_dir "$build_prefix"

  # Get list of executables to run via distcc
  local distrib_apps=$(cd bin; \
                       find . \( -type f -o -type l \) \
                                 -perm -100 \
                              \( -name "*c++" \
                                 -o -name "*g++" \
                                 -o -name "*gcc" \
                                 -o -name "*gcc-[0-9]*[0-9]" \))

  rm -rf distributed
  mkdir distributed
  cd distributed

  # Make symlinks to all subdirs of real directory
  ln -s ../* .
  # but remove symlinks to special cases
  rm bin distributed
  mkdir bin

  # Make symlinks to all apps in real bin
  cd bin
  for app in `cd ../../bin; ls`; do
      ln -s ../../bin/$app .
  done
  # but remove symlinks to special cases
  rm $distrib_apps

  # and create shell scripts for the special cases
  local app
  for app in $distrib_apps; do
    # canonicalize path by getting rid of extra ./ by find .
    app=`echo $app | sed "s,^\./,,g"`
    # use readlink to canonicalize paths in the script, so that distccd
    # receives the absolute path of the real app that this script shims
    cat > $app <<_EOF_
#!/bin/bash
exec distcc "\$(readlink -mn \${0%/*}/../../bin/$app)" "\$@"
_EOF_
    chmod 755 $app 
  done

  pop_dir
}

#
# Usage: strip_libs PREFIX TARGET
#
# Strip shared libraries and static archives using "$PREFIX/bin/strip".
#
strip_libs() {
  [ $# -eq 2 ] || abort "incorrect call syntax"

  local prefix target
  prefix="$1"
  target="$2"

  local file

  # Strip shared libraries.
  for file in $(find "$prefix" -type f -a -exec file '{}' ';' | \
                grep ' shared object,' | \
                sed -n -e 's/^\(.*\):[ 	]*ELF.*, not stripped/\1/p'); do
    "$prefix/bin/strip" --strip-unneeded "$file"
  done

  # Strip debugging symbols from static archives.
  for file in $(find "$prefix" -type f -a -exec file '{}' ';' | \
                grep 'current ar archive' | \
                sed -n -e 's/^\(.*\):[ 	]*current ar archive/\1/p'); do
    "$prefix/bin/strip" -g "$file"
  done
}

#
# Usage: strip_libs_and_make_debuginfo PREFIX DIR_TO_CONVERT
#
# Copy debug symbols from all ELF shared libraries under $DIR_TO_CONVERT
# to debuginfo files.  Strip debug symbols from shared libraries and
# create a GNU debuglink to the debuginfo files.
#
# The debuginfo files are placed in the directory ".debug" in the
# original file's directory.  They are named $orig_name.debug
#
# Uses "$PREFIX/bin/objcopy".
#
strip_libs_and_make_debuginfo() {
  [ $# -eq 2 ] || abort "incorrect call syntax"

  local prefix dir_to_convert
  prefix="$1"
  dir_to_convert="$2"

  local objcopy
  objcopy="$prefix/bin/objcopy"

  local file file_dir file_base debuginfo_dir debuginfo_file

  for file in $(find "$dir_to_convert" \
                     \( -type d -a -name .debug -a -prune \) -o \
                     \( -type f -a -exec file '{}' ';' \) | \
                grep ' ELF .* shared object,' | \
                sed -n -e 's/^\(.*\):[ 	]*ELF.*, not stripped/\1/p' | sort); do
    file_dir=$(dirname "$file")
    file_base=$(basename "$file")
    debuginfo_dir="$file_dir/.debug"
    debuginfo_file="$file_base.debug"

    # Assume that if the file already has a debug link, that it is a hard-linked
    # file and lives in the same directory as its other links.  This may not
    # be correct in general, but is correct for our tools.
    if readelf --sections $file | \
           grep -w '\.gnu_debuglink' > /dev/null 2>&1; then
      echo "skipping debuginfo file for $file (already has one)"
      continue
    fi

    echo "creating debuginfo file for $file"
    mkdir -p "$debuginfo_dir"
    $objcopy --only-keep-debug "$file" "$debuginfo_dir/$debuginfo_file"
    # Clear x bits to keep brp-strip from stripping the .debug file.
    chmod -x "$debuginfo_dir/$debuginfo_file"
    # Note that the .gnu_debuglink section only keeps the file's basename.
    $objcopy \
      --strip-debug \
      --add-gnu-debuglink="$debuginfo_dir/$debuginfo_file" \
      "$file"
  done
}

#
# Usage: strip_exes_and_make_debuginfo PREFIX DIR_TO_CONVERT
#
# Copy debug symbols from all ELF executables under $DIR_TO_CONVERT to
# debuginfo files.  Strip debug symbols from executables and create a
# GNU debuglink to the debuginfo files.
#
# The debuginfo files are placed in the directory ".debug" in the
# original file's directory.  They are named $orig_name.debug
#
# Uses "$PREFIX/bin/objcopy".
#
strip_exes_and_make_debuginfo() {
  [ $# -eq 2 ] || abort "incorrect call syntax"

  local prefix dir_to_convert
  prefix="$1"
  dir_to_convert="$2"

  local objcopy
  objcopy="$prefix/bin/objcopy"

  local file file_dir file_base debuginfo_dir debuginfo_file

  for file in $(find "$dir_to_convert" \
                     \( -type d -a -name .debug -a -prune \) -o \
                     \( -type f -a -exec file '{}' ';' \) | \
                grep ' ELF .* executable,' | \
                sed -n -e 's/^\(.*\):[ 	]*ELF.*, not stripped/\1/p' | sort); do
    file_dir=$(dirname "$file")
    file_base=$(basename "$file")
    debuginfo_dir="$file_dir/.debug"
    debuginfo_file="$file_base.debug"

    # Assume that if the file already has a debug link, that it is a hard-linked
    # file and lives in the same directory as its other links.  This may not
    # be correct in general, but is correct for our tools.
    if readelf --sections $file | \
           grep -w '\.gnu_debuglink' > /dev/null 2>&1; then
      echo "skipping debuginfo file for $file (already has one)"
      continue
    fi

    echo "creating debuginfo file for $file"
    mkdir -p "$debuginfo_dir"
    $objcopy --only-keep-debug "$file" "$debuginfo_dir/$debuginfo_file"
    # Clear x bits to keep brp-strip from stripping the .debug file.
    chmod -x "$debuginfo_dir/$debuginfo_file"
    # Note that the .gnu_debuglink section only keeps the file's basename.
    $objcopy \
      --strip-debug \
      --add-gnu-debuglink="$debuginfo_dir/$debuginfo_file" \
      "$file"
  done
}

#
# Usage: make_symbolic_links INSTALL_DIR TARGET
#
# Convert the files in $INSTALL_DIR/$TARGET/bin into symbolic links to files
# in $INSTALL_DIR/bin.  Normally, these are hard links.  However, this causes
# recent versions of RPM to generate rpmlib(PartialHardlinkSets)
# dependencies, which are incompatible with the RPM version (4.0.2) in
# production.
#
make_symbolic_links() {
  [ $# -eq 2 ] || abort "incorrect call syntax"

  local install_dir target

  install_dir="$1"
  target="$2"

  push_dir "$install_dir/$target/bin"

  local file target_file
  for file in $(find . -maxdepth 1 -type f -links +1); do
    file=$(basename "$file")
    target_file="../../bin/$file"
    [ -f "$target_file" ] || abort "missing \"$PWD/$target_file\""
    cmp "$file" "$target_file" \
      || abort "\"$PWD/$file\" and \"$PWD/$target_file\" differ"

    rm "$file"
    ln -s "$target_file" "$file"
  done

  pop_dir
}

#
# Usage: build_hostlib SRC_DIR BUILD_DIR INSTALL_DIR [CONFIGURE_OPTS...]
#
# Build a host library that is to be used in the GCC build process.
# It is assumed that the library uses a GNU-ish configure script.
# Shared libraries aren't built, because we want these libraries to
# be linked statically into GCC.
#
build_hostlib() {
  local src_dir build_dir install_dir

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  shift 3

  mkdir -p "$build_dir"
  push_dir "$build_dir"

  "$src_dir"/configure --prefix="$install_dir" --disable-shared \
                       --build=$DEFAULT_HOST --host=$DEFAULT_HOST \
                       --target=$DEFAULT_HOST "$@"
  make $PARALLELMFLAGS
  make install

  pop_dir
}

#
# Usage: build_llvm SRC_DIR BUILD_DIR INSTALL_DIR [CONFIGURE_OPTS...]
#
build_llvm() {
  local src_dir build_dir install_dir

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  shift 3

  mkdir -p "$build_dir"
  push_dir "$build_dir"

  "$src_dir"/configure --prefix="$install_dir" "$@"
  make $PARALLELMFLAGS
  make install

  pop_dir
}

#
# Usage: build_gdb SRC_DIR BUILD_DIR INSTALL_DIR TARGET [CONFIGURE_OPTS...]
#
# Build gdb and gdbserver.
#
build_gdb() {
  local src_dir build_dir install_dir target

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  target="$4"
  shift 4

  mkdir -p "$build_dir/gdb"
  push_dir "$build_dir/gdb"

  "$src_dir"/configure --prefix="$install_dir" --build=$DEFAULT_HOST \
                       --target="$target" "$@"
  make $PARALLELMFLAGS all
  make install

  pop_dir

  mkdir -p "$build_dir/gdbserver"
  push_dir "$build_dir/gdbserver"

  CC="$install_dir/bin/$target-gcc" \
  "$src_dir"/gdb/gdbserver/configure --prefix="$install_dir" \
                                     --build=$DEFAULT_HOST --host="$target" \
                                     "$@"
  make $PARALLELMFLAGS all
  make install

  pop_dir
}

#
# Usage: build_gold SRC_DIR BUILD_DIR INSTALL_DIR TARGET [CONFIGURE_OPTS...]
#
build_gold() {
  local src_dir build_dir install_dir target

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  target="$4"
  shift 4

  mkdir -p "$build_dir"
  push_dir "$build_dir"

  "$src_dir"/configure --prefix="$install_dir" --build=$DEFAULT_HOST \
                       --target="$target" --enable-gold "$@"
  make $PARALLELMFLAGS all-gold
  make install-gold

  pop_dir

  make_symbolic_links "$install_dir" $target
}

#
# Usage: build_binutils SRC_DIR BUILD_DIR INSTALL_DIR TARGET [CONFIGURE_OPTS...]
#
build_binutils() {
  local src_dir build_dir install_dir target

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  target="$4"
  shift 4

  local option host build
  for option in "$@"; do
    case "$option" in
      --host=*)
        host=$(echo "$option" | sed -e 's/[-_a-zA-Z0-9]*=//')
        ;;
      --build=*)
        build=$(echo "$option" | sed -e 's/[-_a-zA-Z0-9]*=//')
        ;;
    esac
  done

  local extra_config_opts;
  if [ -z "$host" -a -z "$build" ]; then
    extra_config_opts="--build=$DEFAULT_HOST --host=$DEFAULT_HOST"
  elif [ -z "$host" ]; then
    extra_config_opts="--host=$build"
  elif [ -z "$build" ]; then
    extra_config_opts="--build=$host"
  fi

  mkdir -p "$build_dir"
  push_dir "$build_dir"

  "$src_dir"/configure --prefix="$install_dir" --target="$target" \
                       --disable-nls $extra_config_opts "$@"

  make $PARALLELMFLAGS all
  make install

  pop_dir

  make_symbolic_links "$install_dir" $target
}

#
# Usage: make_deterministic_ar_wrapper INSTALL_DIR WRAPPER_NAME
#
# Make a wrapper around INSTALL_DIR/ar that adds the 'D' (deterministic mode)
# flag, and removes any'u' (update) flag in ar's operation code.
#
# This uses an absolute path to INSTALL_DIR, so is probably not suitable
# for installation as part of a toolchain.
#
make_deterministic_ar_wrapper() {
  local install_dir wrapper_name wrapped_bin

  install_dir="$1"
  wrapper_name="$2"

  wrapped_bin=ar

  rm -f $wrapper_name
  echo "#!/bin/sh" > $wrapper_name
  cat >> $wrapper_name <<__EOF__
  first="\$1"D
  shift
  case "\$first" in
  *u*) first=\`echo "\$first" | sed -e s,u,,g\`
  esac
  exec $install_dir/bin/$wrapped_bin "\$first" "\$@"
__EOF__
  chmod 555 $wrapper_name
}

#
# Usage: make_deterministic_ranlib_wrapper INSTALL_DIR WRAPPER_NAME
#
# Make a wrapper for ranlib suitable for use with ar in deterministic mode.
# In this case, ranlib should do nothing, so the wrapper invokes /bin/true
# instead of ranlib.
#
make_deterministic_ranlib_wrapper() {
  local install_dir wrapper_name

  install_dir="$1"
  wrapper_name="$2"

  rm -f $wrapper_name
  echo "#!/bin/true" > $wrapper_name
  chmod 555 $wrapper_name
}

#
# Usage: archive_ld PREFIX TARGET
#
# Move ld into subdirectories named compat-ld.  This allows
# the binutils ld to be used in cases where gold is insufficient.
#
archive_ld() {
  [ $# -eq 2 ] || abort "incorrect call syntax"

  local prefix target
  prefix="$1"
  target="$2"

  mkdir -p "$prefix/bin/compat-ld"
  mv "$prefix/bin/ld" "$prefix/bin/compat-ld/"

  local target_compat_dir="$prefix/$target/bin/compat-ld"
  mkdir -p "$target_compat_dir"
  push_dir "$target_compat_dir"
  ln -s "../../../bin/compat-ld/ld" ld
  pop_dir

  rm "$prefix/$target/bin/ld"
}

#
# Usage: build_gcc SRC_DIR BUILD_DIR INSTALL_DIR TARGET [CONFIGURE_OPTS...]
#
build_gcc() {
  local src_dir build_dir install_dir target

  src_dir="$1"
  build_dir="$2"
  install_dir="$3"
  target="$4"
  shift 4

  # TODO(cgd): remove once GCC's fortran library build works right.
  # special case: to handle debug prefix mapping, for now we need to override
  # FCFLAGS on the make command line.  We can't do it in the environment
  # (because the variable settings in the makefile will take precedence).
  # So we check for FCFLAGS in our arguments, and if it's present then we
  # special-case the invocation of 'make'.  See bug 1366397.
  local fcflags_to_pass=""

  local option host build
  for option in "$@"; do
    case "$option" in
      --host=*)
        host=$(echo "$option" | sed -e 's/[-_a-zA-Z0-9]*=//')
        ;;
      --build=*)
        build=$(echo "$option" | sed -e 's/[-_a-zA-Z0-9]*=//')
        ;;
      FCFLAGS=*)
        fcflags_to_pass="$option"
        ;;
    esac
  done

  local extra_config_opts;
  if [ -z "$host" -a -z "$build" ]; then
    host=$DEFAULT_HOST
    build=$DEFAULT_HOST
    extra_config_opts="--build=$build --host=$host"
  elif [ -z "$host" ]; then
    host=$build
    extra_config_opts="--host=$host"
  elif [ -z "$build" ]; then
    build=$host
    extra_config_opts="--build=$build"
  fi

  mkdir -p "$build_dir"
  push_dir "$build_dir"

  # --enable-symvers=gnu is really only needed for sh4 to work around a
  # detection problem.  It only matters for gcc-3.2.x and later, I think.
  #
  # --disable-nls works around a crash bug on ppc405, but also embedded
  # systems don't really need message catalogs...
  #
  # --with-gnu-as and --with-gnu-ld control features specific to the
  # GNU assembler and linker and are NOT auto-detected by the compiler
  # configuration process.
  "$src_dir"/configure --prefix="$install_dir" --target=$target \
                       --disable-nls --enable-threads=posix \
                       --enable-symvers=gnu --enable-__cxa_atexit \
                       --enable-c99 --enable-long-long \
                       --with-gnu-as --with-gnu-ld \
                       $extra_config_opts "$@"

  if [ $host != $build ]; then
    make $PARALLELMFLAGS all-build-libiberty || true
  fi

  # TODO(cgd): see comments above.
  if [ -n "$fcflags_to_pass" ]; then
    SHELL=/bin/sh make $PARALLELMFLAGS "$fcflags_to_pass" all
  else
    SHELL=/bin/sh make $PARALLELMFLAGS all
  fi
  make install 

  pop_dir

  make_symbolic_links "$install_dir" $target
}

#
# Usage: create_file_lists RPM_BUILD_ROOT TARGET_TOP RUNTIME_TOP_32 \
#                          RUNTIME_TOP_64
#
# Create file lists to be used for RPM packaging in the current working
# directory.
#
# Layout of the directory that is searched is assumed to be the following:
#
# RPM_BUILD_ROOT/
#    TARGET_TOP/
#       bin/...
#       man/...
#       ...
#       debug-src/...
#    RUNTIME_TOP/
#       ...
#
# Within any of these directories, .debug directories may exist which
# contain debug info files.
#
# This function creates three file lists, named:
#    files.devel
#    files.runtimes
#    files.debuginfo
#
# The "debuginfo" file list includes the debug-src directory and all
# of its contents.
#
# The "runtimes" file list includes all of RUNTIMES except for any
# .debug directories.
#
# Last but not lest, the "devel" file list includes everything else.
#
create_file_lists() {
  local rpm_build_root="$1"
  local top="$2"
  local runtime_top_32="$3"
  local runtime_top_64="$4"

  local target_top="$top/x86"
  local dbgsrc_top="$target_top/debug-src"
  local top_prefix="$rpm_build_root$top"
  local dbgsrc_prefix="$rpm_build_root$dbgsrc_top"
  local target_prefix="$rpm_build_root$target_top"
  local runtime_prefix_32="$rpm_build_root$runtime_top_32"
  local runtime_prefix_64="$rpm_build_root$runtime_top_64"

  # Create devel files list.
  echo "%defattr(-,root,root)" > "files.devel"
  echo "%docdir $target_top/man" >> "files.devel"
  echo "%docdir $target_top/info" >> "files.devel"
  # All directories except the src, runtimes, and .debug dirs.
  find $top_prefix \( -type d -name .debug -prune -o \
                      -type d -wholename "$dbgsrc_prefix" -prune -o \
                      -type d -wholename "$runtime_prefix_32" -prune -o \
                      -type d -wholename "$runtime_prefix_64" -prune -o \
                      -type d -print \) | \
      sed -e "s|^$rpm_build_root||" -e 's|^|%dir |' \
      >> "files.devel"
  # ... and the contents of those directories
  find $top_prefix \( -type d -name .debug -prune -o \
                      -type d -wholename "$dbgsrc_prefix" -prune -o \
                      -type d -wholename "$runtime_prefix_32" -prune -o \
                      -type d -wholename "$runtime_prefix_64" -prune -o \
                      ! -type d -print \) | \
      sed -e "s|^$rpm_build_root||" \
      >> "files.devel"

  # Create runtimes file list.
  echo "%defattr(-,root,root)" > "files.runtimes"
  # Only the runtime tree, but prune any debug directories.
  find $runtime_prefix_32 $runtime_prefix_64 \( -type d -name .debug -prune -o \
                             -type d -print \) | \
      sed -e "s|^$rpm_build_root||" -e 's|^|%dir |' \
      >> "files.runtimes"
  # ... and the contents of those directories
  find $runtime_prefix_32 $runtime_prefix_64 \( -type d -name .debug -prune -o \
                            ! -type d -print \) | \
      sed -e "s|^$rpm_build_root||" \
      >> "files.runtimes"

  # Create the debuginfo file list.  It contains *everyting* in
  # $dbgsrc_prefix and everything in each debug dir.
  echo "%defattr(-,root,root)" > "files.debuginfo"
  echo "$dbgsrc_prefix" | \
      sed -e "s|^$rpm_build_root||" \
      >> "files.debuginfo"
  find $target_prefix $runtime_prefix_32 $runtime_prefix_64 \
       \( -type d -wholename "$dbgsrc_prefix" -prune -o \
          -type d -name .debug -prune -print \) | \
      sed -e "s|^$rpm_build_root||" \
      >> "files.debuginfo"
}

#
# Performs a traditional crosstool build.
#
# Before calling this function, the following required variables must be set:
#
#   PREFIX          toolchain installation prefix
#   BUILD_DIR       directory where tools are built
#   SRC_DIR         directory where the (unpacked) sources reside
#   BINUTILS_DIR    bare name of the binutils source directory
#   GCC_DIR         bare name of the gcc source directory
#   GLIBC_DIR       bare name of the glibc source directory
#   TARGET          Gnu target identifier (e.g. pentium-linux)
#   TARGET_CFLAGS   compiler flags needed when building glibc (-O recommended)
#
# One of these variables must be set:
#
#   LINUX_SANITIZED_HEADER_DIR    bare name of linux-libc-headers directory
#   LINUX_DIR                     bare name of linux source directory
#
# Other variables are optional.
#
build_crosstool() {
  # Execute in a subshell.  Kind of a bummer but this script leaks.
  (
  # Validate required variables.
  test -z "${PREFIX}"           && abort "Please set PREFIX to where you want the toolchain installed."
  test -z "${BUILD_DIR}"        && abort "Please set BUILD_DIR to the directory where the tools are to be built"
  test -z "${SRC_DIR}"          && abort "Please set SRC_DIR to the directory where the source tarballs are to be unpacked"
  test -z "${BINUTILS_DIR}"     && abort "Please set BINUTILS_DIR to the bare filename of the binutils tarball or directory"
  test -z "${GCC_DIR}"          && abort "Please set GCC_DIR to the bare filename of the gcc tarball or directory"
  test -z "${GLIBC_DIR}"        && abort "Please set GLIBC_DIR to the bare filename of the glibc tarball or directory"
  test -z "${TARGET}"           && abort "Please set TARGET to the Gnu target identifier (e.g. pentium-linux)"
  test -z "${TARGET_CFLAGS}"    && abort "Please set TARGET_CFLAGS to any compiler flags needed when building glibc (-O recommended)"

  if test -z "${LINUX_SANITIZED_HEADER_DIR}" ; then
      test -z "${LINUX_DIR}"        && abort "Please set either LINUX_DIR or LINUX_SANITIZED_HEADER_DIR to the bare filename of the tarball or directory containing the kernel headers"
      LINUX_HEADER_DIR="${LINUX_DIR}"
  else
      test -n "${LINUX_DIR}"        && echo "You set both LINUX_DIR and LINUX_SANITIZED_HEADER_DIR - ignoring LINUX_DIR"
      LINUX_HEADER_DIR="${LINUX_SANITIZED_HEADER_DIR}"
  fi


  # Optional variables.
  if test -z "${GCC_CORE_DIR}"; then
      echo "GCC_CORE_DIR not set, so using $GCC_DIR for bootstrap compiler"
      GCC_CORE_DIR="${GCC_DIR}"
  fi
  test -z "${BINUTILS_EXTRA_CONFIG}" && echo "BINUTILS_EXTRA_CONFIG not set, so not passing any extra options to binutils' configure script"
  test -z "${GCC_EXTRA_CONFIG}"      && echo "GCC_EXTRA_CONFIG not set, so not passing any extra options to gcc's configure script"
  test -z "${GLIBC_EXTRA_CONFIG}"    && echo "GLIBC_EXTRA_CONFIG not set, so not passing any extra options to glibc's configure script"
  test -z "${GLIBC_EXTRA_ENV}"       && echo "GLIBC_EXTRA_ENV not set, so not passing any extra environment variables to glibc's configure script"
  test -z "${GLIBC_EXTRA_CC_ARGS}"   && echo "GLIBC_EXTRA_CC_ARGS not set, so not passing any extra options to gcc when building glibc"
  test -z "${EXTRA_TARGET_CFLAGS}"   && echo "EXTRA_TARGET_CFLAGS not set, so not passing any extra cflags to gcc when building glibc"
  test -z "${USE_SYSROOT}"           && echo "USE_SYSROOT not set, so not configuring with --with-sysroot"
  test -z "${GCC_BUILD}"             && echo "GCC_BUILD not set, assuming BUILD=output of config.guess"
  test -z "${GCC_HOST}"              && echo "GCC_HOST not set, assuming HOST=BUILD"
  test -z "${KERNELCONFIG}" && test ! -f ${LINUX_DIR}/.config  && echo  "KERNELCONFIG not set, and no .config file found, so not configuring linux kernel"
  test -z "${KERNELCONFIG}" || test -r "${KERNELCONFIG}"  || abort  "Can't read file KERNELCONFIG = $KERNELCONFIG, please fix."
  test -z "${GCC_LANGUAGES}"         && echo "GCC_LANGUAGES not set, assuming c,c++"
  GCC_LANGUAGES=${GCC_LANGUAGES-"c,c++"}
  BUILD=${GCC_BUILD-`$SRC_DIR/$GCC_DIR/config.guess`}
  test -z "$BUILD" && abort "bug: BUILD not set?!"

  if test -z "${GLIBC_ADDON_OPTIONS}"; then
     echo "GLIBC_ADDON_OPTIONS not set, so guessing addons from GLIBCTHREADS_FILENAME and GLIBCCRYPT_FILENAME"
     # this is lame, need to fix this for nptl later?
     # (nptl is an addon, but it's shipped in the main tarball)
     GLIBC_ADDON_OPTIONS="="
     case "${GLIBCTHREADS_FILENAME}" in
       *linuxthreads*) GLIBC_ADDON_OPTIONS="${GLIBC_ADDON_OPTIONS}linuxthreads," ;;
     esac
     # crypt is only an addon for glibc-2.1.x
     test -z "${GLIBCCRYPT_FILENAME}"   || GLIBC_ADDON_OPTIONS="${GLIBC_ADDON_OPTIONS}crypt,"
  fi

  # Add some default glibc config options if not given by user.  These used to be hardcoded.
  DEFAULT_GLIBC_EXTRA_CONFIG=""
  case "${GLIBC_EXTRA_CONFIG}" in
  *enable-kernel*) ;;
  *) DEFAULT_GLIBC_EXTRA_CONFIG="${DEFAULT_GLIBC_EXTRA_CONFIG} --enable-kernel=2.4.3"
  esac
  case "${GLIBC_EXTRA_CONFIG}" in
  *-tls*) ;;
  *) DEFAULT_GLIBC_EXTRA_CONFIG="${DEFAULT_GLIBC_EXTRA_CONFIG} --without-tls"
  esac
  case "${GLIBC_EXTRA_CONFIG}" in
  *-__thread*) ;;
  *) DEFAULT_GLIBC_EXTRA_CONFIG="${DEFAULT_GLIBC_EXTRA_CONFIG} --without-__thread"
  esac

  # One is forbidden
  test -z "${LD_LIBRARY_PATH}" || abort  "glibc refuses to build if LD_LIBRARY_PATH is set.  Please unset it before running this script."

  # And one is derived if unset.
  test -z "${GLIBCTHREADS_FILENAME}" &&
  GLIBCTHREADS_FILENAME=`echo $GLIBC_DIR | sed 's/glibc-/glibc-linuxthreads-/'`

  # Check for a few prerequisites that have tripped people up.
  awk '/x/' < /dev/null  || abort "You need awk to build a toolchain."
  test -z "${CFLAGS}"    || abort "Don't set CFLAGS, it screws up the build"
  test -z "${CXXFLAGS}"  || abort "Don't set CXXFLAGS, it screws up the build"
  bison --version > /dev/null || abort "You don't have bison installed"
  flex --version > /dev/null || abort "You don't have flex installed"

  #---------------------------------------------------------

  if test "$GCC_HOST" != ""; then
          # Modify $BUILD so gcc never, ever thinks $build = $host
          UNIQUE_BUILD=`echo $BUILD | sed s/-/-build_/`
          CANADIAN_BUILD="--build=$UNIQUE_BUILD"
          echo "canadian cross, configuring gcc & binutils with $CANADIAN_BUILD"
          # make sure we have a host compiler (since $GCC_HOST-gcc won't work)
          "$CC" --version || abort "Must set CC to a compiler targeting $GCC_HOST.  PATH is $PATH"
          "$AR" --version || abort "Must set AR to a version of 'ar' targeting $GCC_HOST.  PATH is $PATH"
          # make sure we have a target compiler (otherwise glibc configure will fail)
          "$TARGET-gcc" --version || abort "Could not execute $TARGET-gcc.  PATH is $PATH"
  else
          GCC_HOST=$BUILD
          CANADIAN_BUILD=""
  fi


  # Modify GCC_HOST to never be equal to $BUILD or $TARGET
  # This strange operation causes gcc to always generate a cross-compiler
  # even if the build machine is the same kind as the host.
  # This is why CC has to be set when doing a canadian cross;
  # you can't find a host compiler by appending -gcc to our whacky $GCC_HOST
  # Kludge: it is reported that the above causes canadian crosses with
  # cygwin hosts to fail, so avoid it just in that one case.  It would be
  # cleaner to just move this into the non-canadian case
  # above, but I'm afraid that might cause some configure script somewhere
  # to decide that since build==host, they could run host binaries.
  #
  # if host is cygwin and this is not a canadian build, modify GCC_HOST
  case "$GCC_HOST,$CANADIAN_BUILD," in
  *cygwin*,?*,) ;;
  *)            GCC_HOST=`echo $GCC_HOST | sed s/-/-host_/` ;;
  esac

  set -ex

  # map TARGET to Linux equivalent
  case $TARGET in
      alpha*)   ARCH=alpha ;;
      arm*)     ARCH=arm ;;
      cris*)    ARCH=cris ;;
      hppa*)    ARCH=parisc ;;
      i*86*|pentium*)    ARCH=i386 ;;
      i4004)    abort "ENOMEM" ;;
      ia64*)    ARCH=ia64 ;;
      mips*)    ARCH=mips ;;
      m68k*)    ARCH=m68k ;;
      powerpc64*) ARCH=ppc64 ;;
      powerpc*) ARCH=ppc ;;
      ppc*)     abort "Target $TARGET incompatible with binutils and gcc regression tests; use target powerpc-* or powerpc64-* instead";;
      s390*)    ARCH=s390 ;;
      sh*)      ARCH=sh ;;
      sparc64*) ARCH=sparc64 ;;
      sparc*)   ARCH=sparc ;;
      vax*)     ARCH=vax ;;
      x86_64*)  ARCH=x86_64 ;;
      *) abort "Bad target $TARGET"
  esac

  # Make all paths absolute (it's so confusing otherwise)
  # FIXME: this doesn't work well with some automounters
  PREFIX=`mkdir -p $PREFIX; cd $PREFIX; pwd`
  BUILD_DIR=`mkdir -p $BUILD_DIR; cd $BUILD_DIR; pwd`
  SRC_DIR=`cd $SRC_DIR; pwd`
  BINUTILS_DIR=`cd ${SRC_DIR}/${BINUTILS_DIR}; pwd`
  GCC_DIR=`cd ${SRC_DIR}/${GCC_DIR}; pwd`
  GCC_CORE_DIR=`cd ${SRC_DIR}/${GCC_CORE_DIR}; pwd`
  LINUX_HEADER_DIR=`cd ${SRC_DIR}/${LINUX_HEADER_DIR}; pwd`
  GLIBC_DIR=`cd ${SRC_DIR}/${GLIBC_DIR}; pwd`

  # Always install the bootstrap gcc (used to build glibc)
  # somewhere it can't interfere with the final gcc.
  CORE_PREFIX=$BUILD_DIR/gcc-core-prefix

  # If user isn't doing a canadian cross, add the target compiler's bin to
  # the path, so we can use the compiler we build to build glibc etc.
  if test "$CANADIAN_BUILD" = ""; then
          PATH="${PREFIX}/bin:$CORE_PREFIX/bin:${PATH}"
          export PATH
  fi

  # test that we have write permissions to the install dir
  mkdir -p ${PREFIX}/${TARGET}
  touch ${PREFIX}/${TARGET}/test-if-write
  test -w ${PREFIX}/${TARGET}/test-if-write || abort "You don't appear to have write permissions to ${PREFIX}/${TARGET}."
  rm -f ${PREFIX}/${TARGET}/test-if-write

  if test -z "$USE_SYSROOT"; then
      # plain old way.  all libraries in prefix/target/lib
      SYSROOT=${PREFIX}/${TARGET}
      HEADERDIR=$SYSROOT/include
      # hack!  Always use --with-sysroot for binutils.
      # binutils 2.14 and later obey it, older binutils ignore it.
      # Lets you build a working 32->64 bit cross gcc
      BINUTILS_SYSROOT_ARG="--with-sysroot=${SYSROOT}"
      # Use --with-headers, else final gcc will define disable_glibc while building libgcc, and you'll have no profiling
      GCC_SYSROOT_ARG_CORE="--without-headers"
      GCC_SYSROOT_ARG="--with-headers=${HEADERDIR}"
      GLIBC_SYSROOT_ARG=prefix=
  else
      # spiffy new sysroot way.  libraries split between
      # prefix/target/sys-root/lib and prefix/target/sys-root/usr/lib
      SYSROOT=${PREFIX}/${TARGET}/sys-root
      HEADERDIR=$SYSROOT/usr/include
      BINUTILS_SYSROOT_ARG="--with-sysroot=${SYSROOT}"
      GCC_SYSROOT_ARG="--with-sysroot=${SYSROOT}"
      GCC_SYSROOT_ARG_CORE=$GCC_SYSROOT_ARG
      GLIBC_SYSROOT_ARG=""
      # glibc's prefix must be exactly /usr, else --with-sysroot'd
      # gcc will get confused when $sysroot/usr/include is not present
      # Note: --prefix=/usr is magic!  See http://www.gnu.org/software/libc/FAQ.html#s-2.2
  fi

  # Make lib directory in sysroot, else the ../lib64 hack used by 32 -> 64 bit
  # crosscompilers won't work, and build of final gcc will fail with 
  #  "ld: cannot open crti.o: No such file or directory"
  mkdir -p $SYSROOT/lib
  mkdir -p $SYSROOT/usr/lib

  echo
  echo "Building for --target=$TARGET, --prefix=$PREFIX"

  #---------------------------------------------------------
  # Use sanitized headers, if available
  if test -z "$LINUX_SANITIZED_HEADER_DIR" ; then
      echo Prepare kernel headers
  else
      echo Copy sanitized headers
  fi

  cd $LINUX_HEADER_DIR
  mkdir -p $HEADERDIR

  # no indentation for now because indentation levels are rising too high
  if test -z "$LINUX_SANITIZED_HEADER_DIR" ; then

  if test -f "$KERNELCONFIG" ; then
      cp $KERNELCONFIG .config
  fi
  if test -f .config; then
      yes "" | make ARCH=$ARCH oldconfig
  fi

  # autodetect kernel version from contents of Makefile
  KERNEL_VERSION=`awk '/^VERSION =/ { print $3 }' $LINUX_HEADER_DIR/Makefile`
  KERNEL_PATCHLEVEL=`awk '/^PATCHLEVEL =/ { print $3 }' $LINUX_HEADER_DIR/Makefile`

  case "$KERNEL_VERSION.$KERNEL_PATCHLEVEL.x" in
  2.2.x|2.4.x) make ARCH=$ARCH symlinks    include/linux/version.h
               ;;
  2.6.x)       case $ARCH in
               sh*)        # sh does secret stuff in 'make prepare' that can't be triggered separately,
                           # but happily, it doesn't use target gcc, so we can use it.
                           # Update: this fails on 2.6.11, as it installs elfconfig.h, which requires target compiler :-(
                           make ARCH=$ARCH prepare include/linux/version.h
                           ;;
               arm*|cris*) make ARCH=$ARCH include/asm include/linux/version.h include/asm-$ARCH/.arch
                           ;;
               mips*)      # for linux-2.6, 'make prepare' for mips doesn't 
                           # actually create any symlinks.  Hope generic is ok.
                           # Note that glibc ignores all -I flags passed in CFLAGS,
                           # so you have to use -isystem.
                           make ARCH=$ARCH include/asm include/linux/version.h
                           TARGET_CFLAGS="$TARGET_CFLAGS -isystem $LINUX_HEADER_DIR/include/asm-mips/mach-generic"
                           ;;
               *)          make ARCH=$ARCH include/asm include/linux/version.h
                           ;;
               esac
               ;;
  *)           abort "Unsupported kernel version $KERNEL_VERSION.$KERNEL_PATCHLEVEL"
  esac
  cp -r include/asm-generic $HEADERDIR/asm-generic

  fi # test -z "$LINUX_SANITIZED_HEADER_DIR"

  cp -r include/linux $HEADERDIR
  cp -r include/asm-${ARCH} $HEADERDIR/asm

  cd $BUILD_DIR

  #---------------------------------------------------------
  echo Build binutils

  build_binutils "$BINUTILS_DIR" "$BUILD_DIR/build-binutils" \
                 "$PREFIX" "$TARGET" $CANADIAN_BUILD --host=$GCC_HOST \
                 ${BINUTILS_EXTRA_CONFIG} $BINUTILS_SYSROOT_ARG

  if test x"$CORE_PREFIX" != x"$PREFIX"; then
      # if we're using a different core compiler, make binutils available to it
      # gcc searches in $CORE_PREFIX/$TARGET/bin for tools like 'ar', 'as', and 'ld'
      # instead of the location its configure script claims it searches (gcc_cv_as), grr
      mkdir -p $CORE_PREFIX/$TARGET/bin
      for tool in ar as ld strip; do
         # Remove old symlink to avoid clash on rerun
         # ln -snf is safe, but not portable.  
         # Can't test for existence of symlinks reliably
         # rm -f returns nonzero status on Solaris if it fails, so || true to keep script from aborting
         rm -f $CORE_PREFIX/$TARGET/bin/$tool || true
         ln -s $PREFIX/bin/$TARGET-$tool $CORE_PREFIX/$TARGET/bin/$tool
      done
  fi

  # test to see if this step passed
  logresult binutils ${PREFIX}/bin/${TARGET}-ld

  #---------------------------------------------------------
  echo "Install glibc headers needed to build bootstrap compiler -- but only if gcc-3.x"

  # Only need to install bootstrap glibc headers for gcc-3.0 and above?  Or maybe just gcc-3.3 and above?
  # See also http://gcc.gnu.org/PR8180, which complains about the need for this step.
  # Don't install them if they're already there (it's really slow)
  if grep -q 'gcc-[34]' ${GCC_CORE_DIR}/ChangeLog && test '!' -f $HEADERDIR/features.h; then
      mkdir -p build-glibc-headers; cd build-glibc-headers

      if test '!' -f Makefile; then
          # The following three things have to be done to build glibc-2.3.x, but they don't hurt older versions.
          # 1. override CC to keep glibc's configure from using $TARGET-gcc. 
          # 2. disable linuxthreads, which needs a real cross-compiler to generate tcb-offsets.h properly
          # 3. build with gcc 3.2 or later
          # Compare these options with the ones used when building glibc for real below - they're different.
          # As of glibc-2.3.2, to get this step to work for hppa-linux, you need --enable-hacker-mode
          # so when configure checks to make sure gcc has access to the assembler you just built...
          # Alternately, we could put ${PREFIX}/${TARGET}/bin on the path.
          # Set --build so maybe we don't have to specify "cross-compiling=yes" below (haven't tried yet)
          # Note: the warning
          # "*** WARNING: Are you sure you do not want to use the `linuxthreads'"
          # *** add-on?"
          # is ok here, since all we want are the basic headers at this point.
          # Override libc_cv_ppc_machine so glibc-cvs doesn't complain
          # 'a version of binutils that supports .machine "altivec" is needed'.
          libc_cv_ppc_machine=yes \
          CC=gcc-3.3 \
              ${GLIBC_DIR}/configure --prefix=/usr \
              --build=$BUILD --host=$TARGET \
              --without-cvs --disable-sanity-checks --with-headers=$HEADERDIR \
              --enable-hacker-mode
      fi

      if grep -q GLIBC_2.3 ${GLIBC_DIR}/ChangeLog; then
          # glibc-2.3.x passes cross options to $(CC) when generating errlist-compat.c, which fails without a real cross-compiler.
          # Fortunately, we don't need errlist-compat.c, since we just need .h files, 
          # so work around this by creating a fake errlist-compat.c and satisfying its dependencies.
          # Another workaround might be to tell configure to not use any cross options to $(CC).
          # The real fix would be to get install-headers to not generate errlist-compat.c.
          # Note: BOOTSTRAP_GCC is used by patches/glibc-2.3.5/glibc-mips-bootstrap-gcc-header-install.patch
          libc_cv_ppc_machine=yes \
                  make CFLAGS=-DBOOTSTRAP_GCC sysdeps/gnu/errlist.c
          mkdir -p stdio-common
          # sleep for 2 seconds for benefit of filesystems with lousy time resolution, like FAT,
          # so make knows for sure errlist-compat.c doesn't need generating
          sleep 2
          touch stdio-common/errlist-compat.c
      fi
      # Note: BOOTSTRAP_GCC is used by patches/glibc-2.3.5/glibc-mips-bootstrap-gcc-header-install.patch
      libc_cv_ppc_machine=yes \
      make cross-compiling=yes install_root=${SYSROOT} CFLAGS=-DBOOTSTRAP_GCC $GLIBC_SYSROOT_ARG install-headers

      # Two headers -- stubs.h and features.h -- aren't installed by install-headers,
      # so do them by hand.  We can tolerate an empty stubs.h for the moment.
      # See e.g. http://gcc.gnu.org/ml/gcc/2002-01/msg00900.html

      mkdir -p $HEADERDIR/gnu
      touch $HEADERDIR/gnu/stubs.h
      cp ${GLIBC_DIR}/include/features.h $HEADERDIR/features.h
      # Building the bootstrap gcc requires either setting inhibit_libc, or
      # having a copy of stdio_lim.h... see
      # http://sources.redhat.com/ml/libc-alpha/2003-11/msg00045.html
      cp bits/stdio_lim.h $HEADERDIR/bits/stdio_lim.h

      # Following error building gcc-4.0.0's gcj:
      #  error: bits/syscall.h: No such file or directory
      # solved by following copy; see
      # http://sourceware.org/ml/crossgcc/2005-05/msg00168.html
      # but it breaks arm, see http://sourceware.org/ml/crossgcc/2006-01/msg00091.html
      # so uncomment this if you need it
      cp misc/syscall-list.h $HEADERDIR/bits/syscall.h

      cd ..
  fi

  #---------------------------------------------------------
  echo "Build gcc-core (just enough to build glibc)"

  mkdir -p build-gcc-core; cd build-gcc-core

  echo Copy headers to install area of bootstrap gcc, so it can build libgcc2
  mkdir -p $CORE_PREFIX/$TARGET/include
  cp -r $HEADERDIR/* $CORE_PREFIX/$TARGET/include

  # Use --with-local-prefix so older gccs don't look in /usr/local (http://gcc.gnu.org/PR10532)
  # Use funky prefix so it doesn't contaminate real prefix, in case GCC_DIR != GCC_CORE_DIR

  if test '!' -f Makefile; then
      ${GCC_CORE_DIR}/configure $CANADIAN_BUILD --target=$TARGET --host=$GCC_HOST --prefix=$CORE_PREFIX \
          --with-local-prefix=${SYSROOT} \
          --disable-multilib \
          --with-newlib \
          ${GCC_EXTRA_CONFIG} \
          ${GCC_SYSROOT_ARG_CORE} \
          --disable-nls \
          --enable-threads=no \
          --enable-symvers=gnu \
          --enable-__cxa_atexit \
          --enable-languages=c \
          --disable-shared
  fi

  test "$CANADIAN_BUILD" = "" || make $PARALLELMFLAGS all-build-libiberty || true
  SHELL=/bin/sh make $PARALLELMFLAGS all-gcc 
  make install-gcc

  # Create symbolic links mapping libgcc_eh.a to libgcc.a.  This is required
  # to build glibc later.
  locale libgcc libgcc_eh
  for libgcc in $(find "$CORE_PREFIX" -name libgcc.a); do
    libgcc_eh="$(dirname "$libgcc")/libgcc_eh.a"
    [ -e "$libgcc_eh" ] || ln -s "$libgcc" "$libgcc_eh"
  done

  cd ..

  logresult gcc-core $CORE_PREFIX/bin/${TARGET}-gcc

  #---------------------------------------------------------
  echo Build glibc and linuxthreads

  mkdir -p build-glibc; cd build-glibc

  # sh4 really needs to set configparms as of gcc-3.4/glibc-2.3.2
  # note: this is awkward, doesn't work well if you need more than one line in configparms
  echo ${GLIBC_CONFIGPARMS} > configparms

  if test '!' -f Makefile; then
      # Configure with --prefix the way we want it on the target...
      # There are a whole lot of settings here.  You'll probably want
      # to read up on what they all mean, and customize a bit, possibly by setting GLIBC_EXTRA_CONFIG
      # Compare these options with the ones used when installing the glibc headers above - they're different.
      # Adding "--without-gd" option to avoid error "memusagestat.c:36:16: gd.h: No such file or directory" 
      # See also http://sources.redhat.com/ml/libc-alpha/2000-07/msg00024.html. 
      # Set BUILD_CC, or you won't be able to build datafiles
      # Set --build, else glibc-2.3.2 will think you're not cross-compiling, and try to run the test programs

      # For glibc 2.3.4 and later we need to set some autoconf cache
      # variables, because nptl/sysdeps/pthread/configure.in does not
      # work when cross-compiling.
      if test -d ${GLIBC_DIR}/nptl; then
          libc_cv_forced_unwind=yes
          libc_cv_c_cleanup=yes
          export libc_cv_forced_unwind libc_cv_c_cleanup
      fi

      BUILD_CC=gcc CFLAGS="$TARGET_CFLAGS $EXTRA_TARGET_CFLAGS" CC="${TARGET}-gcc $GLIBC_EXTRA_CC_ARGS" \
      AR=${TARGET}-ar RANLIB=${TARGET}-ranlib \
          ${GLIBC_DIR}/configure --prefix=/usr \
          --build=$BUILD --host=$TARGET \
          ${GLIBC_EXTRA_CONFIG} ${DEFAULT_GLIBC_EXTRA_CONFIG} \
          --without-cvs --disable-profile --disable-debug --without-gd \
          --enable-add-ons${GLIBC_ADDON_OPTIONS} --with-headers=$HEADERDIR
  fi

  # If this fails with an error like this:
  # ...  linux/autoconf.h: No such file or directory 
  # then you need to set the KERNELCONFIG variable to point to a .config file for this arch.
  # The following architectures are known to need kernel .config: alpha, arm, ia64, s390, sh, sparc
  # Note: LD and RANLIB needed by glibc-2.1.3's c_stub directory, at least on macosx
  # No need for PARALLELMFLAGS here, Makefile already reads this environment variable
  make LD=${TARGET}-ld RANLIB=${TARGET}-ranlib all
  make install_root=${SYSROOT} $GLIBC_SYSROOT_ARG install

  # This doesn't seem to work when building a crosscompiler,
  # as it tries to execute localedef using the just-built ld.so!?
  #make localedata/install-locales install_root=${SYSROOT}

  # Fix problems in linker scripts.
  # 
  # 1. Remove absolute paths
  # Any file in a list of known suspects that isn't a symlink is assumed to be a linker script.
  # FIXME: test -h is not portable
  # FIXME: probably need to check more files than just these three...
  # Need to use sed instead of just assuming we know what's in libc.so because otherwise alpha breaks
  #
  # 2. Remove lines containing BUG per http://sources.redhat.com/ml/bug-glibc/2003-05/msg00055.html,
  # needed to fix gcc-3.2.3/glibc-2.3.2 targeting arm
  #
  # To make "strip *.so.*" not fail (ptxdist does this), rename to .so_orig rather than .so.orig
  for file in libc.so libpthread.so libgcc_s.so; do
      for lib in lib lib64 usr/lib usr/lib64; do
        if test -f ${SYSROOT}/$lib/$file && test ! -h ${SYSROOT}/$lib/$file; then
          mv ${SYSROOT}/$lib/$file ${SYSROOT}/$lib/${file}_orig
          sed 's,/usr/lib/,,g;s,/usr/lib64/,,g;s,/lib/,,g;s,/lib64/,,g;/BUG in libc.scripts.output-format.sed/d' < ${SYSROOT}/$lib/${file}_orig > ${SYSROOT}/$lib/$file
        fi
      done
  done
  cd ..

  test -f ${SYSROOT}/lib/libc.a || test -f ${SYSROOT}/lib64/libc.a || test -f ${SYSROOT}/usr/lib/libc.a || test -f ${SYSROOT}/usr/lib64/libc.a || abort Building libc failed

  #---------------------------------------------------------
  echo Build final gcc

  build_gcc "$GCC_DIR" "$BUILD_DIR/build-gcc" "$PREFIX" $TARGET \
            $CANADIAN_BUILD --host=$GCC_HOST ${GCC_EXTRA_CONFIG} \
            $GCC_SYSROOT_ARG --with-local-prefix=${SYSROOT} \
            --enable-languages="$GCC_LANGUAGES"

  logresult "final gcc" ${PREFIX}/bin/${TARGET}-gcc

  #---------------------------------------------------------

  echo Cross-toolchain build complete.  Result in ${PREFIX}.
  )
}

# Copy debug sources, but prune source which are not
# useful for debugging. See http://b/1416593
copy_debug_sources() {
  [ $# -eq 2 ] || abort "incorrect call syntax"
  local src=$1
  local dst=$2
  [[ -z "$src" ]] && abort "empty src"
  [[ -z "$dst" ]] && abort "empty dst"

  push_dir "$src" &&
  find . \
    \( -type d -name 'tests' -prune \) -o \
    \( -type d -name 'testsuite' -prune \) -o \
    \( -type d -name 'java' -prune \) -o \
    \( -type d -name 'libjava' -prune \) -o \
    \( -type d -name 'examples' -prune \) -o \
    -print | cpio -pdm "$dst" &&
  pop_dir
}

#
# Usage: build_mao SRC_DIR BUILD_DIR INSTALL_DIR TARGET \
#                  BINUTILS_SRC_DIR BINUTILS_BUILD_DIR
#
build_mao() {
  [ $# -eq 6 ] || abort "incorrect call syntax"
  local src_dir=$1
  local build_dir=$2
  local install_dir=$3
  local target=$4
  local binutils_src_dir=$5
  local binutils_build_dir=$6

  # The mao build process has no configure step and its Makefile sets a
  # bunch of variables, we need to configure all of those variables via
  # the make command line.
  local -a mao_make_args=(
    CC="$CC"
    TARGET="$target"
    LOCALEDIR="$install_dir/share"
    BINUTILSRC="$binutils_src_dir"
    BINUTILOBJ="$binutils_build_dir"
    PYTHON=""
    PYTHONLIB=""
    PYTHONINCL=""
    PYTHONLDOPTS=""
  )

  # We need to make the build directory and tell the mao build to put its
  # outputs there.  Also, the program name it tries to install is not
  # appropriate, so we have it install in its build directory, and install
  # manually later.
  mkdir -p $build_dir
  mao_make_args+=(
    SRCDIR="$src_dir/src"
    OBJDIR="$build_dir"
    BINDIR="$build_dir"
    HEADERDIR="$build_dir/include"
  )

  # And, do the build.  This creates the file mao-$target in BUILD_DIR.
  push_dir "$build_dir"
  make $PARALLELMFLAGS -f "$src_dir/src/Makefile" "${mao_make_args[@]}"
  make -f "$src_dir/src/Makefile" "${mao_make_args[@]}" headers
  pop_dir

  # Install the mao binary under INSTALL_DIR, with a symlink as is done
  # for the other GNU tools.  (This will be used by mao's as wrapper.)
  mkdir -p "$install_dir/bin"
  cp -p "$build_dir/mao-$target" "$install_dir/bin/mao"
  cp -a "$build_dir/include" "$install_dir/mao-include"
  chmod -R o+r "$install_dir/mao-include"
  mkdir -p "$install_dir/$target/bin"
  ln -s "../../bin/mao" "$install_dir/$target/bin/mao"
}

#
# Usage: wrap_gcc_with_clang PREFIX TEMPLATE INSTALL_DIR
#
# Changes gcc and g++ to be scripts that preprocess the input with clang and
# compile with gcc.
#
wrap_gcc_with_clang() {
  [ $# -eq 3 ] || abort "incorrect call syntax"
  local prefix=$1
  local template=$2
  local install_dir=$3

  echo $prefix
  echo $template
  echo $install_dir

  push_dir $prefix/bin
  mv gcc original-gcc
  mv g++ original-g++
  sed \
    -e "s|CLANG|$install_dir/x86/bin/clang|" \
    -e "s|GCC|$install_dir/x86/bin/original-gcc|" \
    < $template > gcc
  chmod 755 gcc
  cp gcc g++
  pop_dir
}

#
# Usage: make_traditional_crosstool_layout RPMBUILD INSTALL_PREFIX GCC_DIR
#
# Creates symlinks and scripts that emulate the old layout used by
# previous versions of crosstool.
#
make_traditional_crosstool_layout() {
  [ $# -eq 3 ] || abort "incorrect call syntax"
  local rpmbuild=$1
  local top=$2
  local gcc_dir=$3

  local old_top=$top/$gcc_dir

  local top_prefix=$rpmbuild/$top
  local old_top_prefix=$rpmbuild/$old_top
  local x86_dir=$old_top/x86
  local x86_prefix=$rpmbuild/$x86_dir

  # Will be replaced by a script.
  rm $x86_prefix/bin/x86_64-unknown-linux-gnu-*

  local all_apps=$(cd $x86_prefix/bin; find . -type f -perm -100)
  local gcc_apps=$(cd $x86_prefix/bin; \
                   find . -type f -perm -100 \
                    \(    -name "c++" \
                          -o -name "gfortran" \
                          -o -name "g++" \
                          -o -name "cpp" \
                          -o -name "gcc" \
                          -o -name "gcc-[0-9]*[0-9]" \))

  for target in i686-unknown-linux-gnu x86_64-unknown-linux-gnu; do
    local target_prefix=$old_top_prefix/$target
    local target_libdir

    case $target in
    i686-unknown-linux-gnu)
      target_libdir=lib
      target_gcc_opt=-m32
      ;;
    x86_64-unknown-linux-gnu)
      target_libdir=lib64
      target_gcc_opt=-m64
      ;;
    esac
    local runtime_prefix=$top_prefix/$target/$target_libdir

    ln -s x86 $target_prefix

    mkdir -p $runtime_prefix
    cp -a $x86_prefix/$target_libdir/*.so* $runtime_prefix

    # Used by blaze for setting rpath
    mkdir -p $x86_prefix/$target
    ln -s ../$target_libdir $x86_prefix/$target

    for app in $all_apps
    do
      dir=$(dirname $app)
      app=$(basename $app)
      target_app=$x86_prefix/bin/$dir/$target-$app
      [ -e $target_app -o -L $target_app ] && rm $target_app
      ln -s "$app" "$target_app"
    done

    for app in $gcc_apps
    do
      # canonicalize path by getting rid of extra ./ by find .
      app=`echo $app | sed "s,^\./,,g"`
      target_app=$x86_prefix/bin/$target-$app
      [ -e $target_app -o -L $target_app ] && rm $target_app
      cat <<EOF > $target_app
#!/bin/bash
exec \${0%/*}/$app -no-canonical-prefixes $target_gcc_opt "\$@"
EOF
      chmod 755 $target_app
    done

  done
  make_distcc_masquerade_dir $x86_prefix
}

#
# Usage: wrap_gas_with_mao MAO_SRC_DIR INSTALL_DIR TARGET
#
# Moves the GNU assembler binaries into 'compat-as' subdirectories.
# Installs the mao wrapper script as 'as', and tweaks it so that it
# can find the mao and GNU as binaries as we've installed them.
#
wrap_gas_with_mao() {
  [ $# -eq 3 ] || abort "incorrect call syntax"
  local mao_src_dir=$1
  local install_dir=$2
  local target=$3

  # Move the existing 'as' binaries into a compat-as subdir.
  mkdir -p "$install_dir/bin/compat-as"
  mv "$install_dir/bin/as" "$install_dir/bin/compat-as/as"
  rm -f "$install_dir/$target/bin/as"
  mkdir -p "$install_dir/$target/bin/compat-as"
  ln -s "../../../bin/compat-as/as" \
    "$install_dir/$target/bin/compat-as/as"

  # Copy the mao wrapper into place as 'as' so that it will be used
  # by the compiler.  Adjust the script so that the binaries used for
  # mao and GNU as are correct.
  sed \
    -e "/local mao_bin=/s,/mao\$,/mao," \
    -e "/local as_bin=/s,/as-orig\$,/compat-as/as," \
    < $mao_src_dir/scripts/as > "$install_dir/bin/as"
  chmod 755 "$install_dir/bin/as"
  sed \
    -e "/local as_bin=/s,/as-orig\$,/compat-as/as," \
    < $mao_src_dir/scripts/as > "$install_dir/$target/bin/as"
  chmod 755 "$install_dir/$target/bin/as"
}
