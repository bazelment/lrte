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

# Source0: clang-llvm-3.6-svn20100801.tgz
BuildRoot: %{_tmppath}/%{name}-buildroot

# Create debuginfo unless disable_debuginfo is defined.
%define make_debuginfo %{?disable_debuginfo:""}%{!?disable_debuginfo:"t"}

# Remove BuildRoot in %clean unless keep_buildroot is defined.
%define remove_buildroot %{?keep_buildroot:""}%{!?keep_buildroot:"t"}

%description
Clang %{crosstool_clang_version} to work with %{grte_basename}

%prep
# %setup

%define crosstool_top /usr/crosstool/%{crosstool_version}
%define target_top %{crosstool_top}/%{gcc_glibc_version}
%define grte_top %{grte_root}

%build
export PATH="%{target_top}/x86/bin:%{grte_top}/bin:%{grte_top}/sbin:$PATH"
export CC="gcc -isystem %{grte_top}/include -L%{grte_top}/lib64"
export LDFLAGS="-Wl,-I,%{grte_top}/lib64/ld-linux-x86-64.so.2"
export CFLAGS="-isystem %{grte_top}/include -L%{grte_top}/lib64"
WORK_DIR="$RPM_BUILD_DIR/$RPM_PACKAGE_NAME-$RPM_PACKAGE_VERSION"
mkdir -p ${WORK_DIR}/llvm-build
cd ${WORK_DIR}/llvm-build
%{_sourcedir}/llvm/configure \
    --enable-cxx11 \
    --enable-optimized \
    --disable-docs \
    --with-default-sysroot=%{grte_top} \
    --with-build-sysroot=%{grte_top} \
    --prefix=%{target_top}/x86 \
    --build=x86_64-unknown-linux-gnu \
    --host=x86_64-unknown-linux-gnu \
    --enable-targets=host \
    --enable-linker-build-id \
    --includedir=%{grte_top}/include \
    --oldincludedir=%{grte_top}/include \
    --with-gcc-toolchain=%{target_top}/x86 \
    --with-binutils-include=%{target_top}/x86/include \
    CPPFLAGS="-isystem %{grte_top}/include -DGRTE_ROOT='\"%{grte_root}\"'"
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
- Clang %{crosstool_clang_version}.
