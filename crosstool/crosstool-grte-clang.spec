%define gcc_glibc_version gcc-%{grte_gcc_version}-%{grte_basename}
%define base_summary Clang %{crosstool_clang_version} for %{grte_root} with %{gcc_glibc_version}
%define _unpackaged_files_terminate_build 1
%define __os_install_post %{nil}

Summary: %{base_summary}
Name: %{grte_basename}-crosstool%{crosstool_version}-clang-%{crosstool_clang_version}
Version: %{crosstool_rpmver}
Release: %{crosstool_rpmrel}
License: BSD
Group: Development/Languages
Packager: Release Engineer <%{maintainer_email}>
AutoReqProv: no
Requires: %{grte_basename}-runtime %{grte_basename}-headers %{grte_basename}-crosstool%{crosstool_version}-gcc-%{crosstool_gcc_version}

# Source0: cmake-3.2.3.tar.gz
BuildRoot: %{_tmppath}/%{name}-buildroot

# Create debuginfo unless disable_debuginfo is defined.
%define make_debuginfo %{?disable_debuginfo:""}%{!?disable_debuginfo:"t"}

# Remove BuildRoot in %clean unless keep_buildroot is defined.
%define remove_buildroot %{?keep_buildroot:""}%{!?keep_buildroot:"t"}

%description
Clang %{crosstool_clang_version} to work with %{grte_basename}

%prep
# %setup -c
# %setup -T -D -a 0

%define crosstool_top /usr/crosstool/%{crosstool_version}
%define target_top %{crosstool_top}/%{gcc_glibc_version}
%define grte_top %{grte_root}

%build
export PATH="%{target_top}/x86/bin:%{grte_top}/bin:%{grte_top}/sbin:$PATH"
# export CC="gcc -isystem %{grte_top}/include -L%{grte_top}/lib64"
# export LDFLAGS="-Wl,-I,%{grte_top}/lib64/ld-linux-x86-64.so.2"
# export CFLAGS="-isystem %{grte_top}/include -L%{grte_top}/lib64"
# export CPPFLAGS="-isystem %{grte_top}/include -DGRTE_ROOT='\"%{grte_root}\"'"
WORK_DIR="$RPM_BUILD_DIR/$RPM_PACKAGE_NAME-$RPM_PACKAGE_VERSION"

# Build cmake because cmake in ubuntu 13 is too old
# mkdir -p ${WORK_DIR}/cmake
# cd ${WORK_DIR}/cmake
# $WORK_DIR/cmake-3.2.3/configure --parallel=${PARALLELMFLAGS}
# make ${PARALLELMFLAGS}
# make install

mkdir -p ${WORK_DIR}/llvm-build
cd ${WORK_DIR}/llvm-build
cmake -DCMAKE_BUILD_TYPE=Release \
    -DCLANG_GRTE_ROOT=%{grte_root} \
    -DCMAKE_INSTALL_PREFIX=%{target_top}/x86 \
    -DLLVM_TARGETS_TO_BUILD=host \
    -DLLVM_PARALLEL_COMPILE_JOBS=$PARALLELMFLAGS \
    -DLLVM_BUILD_DOCS=OFF \
    -DLLVM_TOOL_LIBCXX_BUILD=OFF \
    -DLLVM_TOOL_LIBCXXABI_BUILD=OFF \
    -DLLVM_TOOL_DRAGONEGG_BUILD=OFF \
    -DLLVM_TOOL_LLGO_BUILD=OFF \
    -DLLVM_TOOL_LLD_BUILD=OFF \
    -DLLVM_TOOL_LLDB_BUILD=OFF \
    -DLLVM_TOOL_LIBUNWIND_BUILD=OFF \
    -DDEFAULT_SYSROOT=%{grte_top} \
    -DGCC_INSTALL_PREFIX=%{target_top}/x86 \
    -DLLVM_BINUTILS_INCDIR=%{target_top}/x86/include \
    %{_sourcedir}/llvm
make $PARALLELMFLAGS
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%install
# Set PATH here so the scripts run by __spec_install_post, which use
# 'strip' from PATH, use the GRTE 'strip'.
export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"

%clean

%files
%defattr(-,root,root)
%{target_top}/x86/bin/*
%{target_top}/x86/include/*
%{target_top}/x86/lib/*
%{target_top}/x86/share/*

%changelog
* Mon Jun 01 2015 Release Engineer <%{maintainer_email}>
- Clang %{crosstool_clang_version} with SVN %{clang_svn_version}.
