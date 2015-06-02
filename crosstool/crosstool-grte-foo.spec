%define gcc_glibc_version gcc-%{grte_gcc_version}-%{grte_basename}
%define base_summary %{gcc_glibc_version} compiler for %{grte_root}
Summary: %{base_summary}
Name: %{grte_basename}-crosstool%{crosstool_version}-foo-%{crosstool_gcc_version}
Version: %{crosstool_rpmver}
Release: %{crosstool_rpmrel}
License: GPL/LGPL
Group: Development/Languages
Packager: Release Engineer <%{maintainer_email}>
AutoReqProv: no

BuildRoot: %{_tmppath}/%{name}-buildroot

# Create debuginfo unless disable_debuginfo is defined.
%define make_debuginfo %{?disable_debuginfo:""}%{!?disable_debuginfo:"t"}
%define debug_cflags %{?disable_debuginfo:""}%{!?disable_debuginfo:"-g"}

# Remove BuildRoot in %clean unless keep_buildroot is defined.
%define remove_buildroot %{?keep_buildroot:""}%{!?keep_buildroot:"t"}

# Enable bootstrapping unless disable_bootstrap is defined.
%define bootstrap_config_arg %{?disable_bootstrap:"--disable-bootstrap"}%{!?disable_bootstrap:""}

%description
GCC %{crosstool_gcc_version} to work with %{grte_basename}, @svn %{gcc_svn_version}

%prep

%define crosstool_top /usr/crosstool/%{crosstool_version}
%define target_top %{crosstool_top}/%{gcc_glibc_version}
%define grte_top %{grte_root}

%build
export PATH="%{grte_top}/bin:%{grte_top}/sbin:$PATH"
WORK_DIR="$RPM_BUILD_DIR/$RPM_PACKAGE_NAME-$RPM_PACKAGE_VERSION"

TARGET=x86_64-unknown-linux-gnu
PREFIX="$RPM_BUILD_ROOT%{target_top}/x86"
# Make gold the default linker
mkdir -p ${PREFIX}
date >  ${PREFIX}/foo

%install

%clean

%files

%defattr(-,root,root)
%{target_top}/x86/foo

%changelog
* Mon Jun 01 2015 Ming Zhao <mzhao@luminatewireless.com>
- Test only.
