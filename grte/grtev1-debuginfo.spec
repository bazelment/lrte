%define _tmppath	%{GRTEBUILD}
%define _topdir		%{GRTEBUILD}
%define _rpmtopdir	%{GRTEBUILD}
%define _builddir	%{GRTEBUILD}/grtev%{grte_version}-debuginfo
%define _rpmdir		%{_rpmtopdir}
%define _sourcedir	%{_rpmtopdir}
%define _specdir	%{_rpmtopdir}
%define _srcrpmdir	%{_rpmtopdir}
%define _build_name_fmt	%{name}-%{version}-%{release}.%{arch}.rpm
%define _unpackaged_files_terminate_build 1
%define __os_install_post %{nil}

Summary: Google Runtime Environment (GRTE) Version %{grte_version} Debug Symbols
Name: %{grte_basename}-debuginfo
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-debuginfo
AutoReqProv: no
Packager: Release Engineer <%{EMAIL}>

%description
Debug symbols for the libaries in the %{grte_basename}-runtimes package.

%prep

%build

%install

%post

%files
%defattr(-,root,root)
%{grte_root}/bin/.debug
%{grte_root}/debug-src
%{grte_root}/lib64/.debug
%{grte_root}/lib64/gconv/.debug
%{grte_root}/libexec/gcc/x86_64-linux-gnu/4.9.1/.debug
%{grte_root}/libexec/gcc/x86_64-linux-gnu/4.9.1/install-tools/.debug
%{grte_root}/libexec/gcc/x86_64-linux-gnu/4.9.1/plugin/.debug
%{grte_root}/sbin/.debug
%{grte_root}/x86_64-linux-gnu/bin/.debug

%include %{grte_changelog}
