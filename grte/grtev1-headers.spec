%define _tmppath	%{GRTEBUILD}
%define _topdir		%{GRTEBUILD}
%define _rpmtopdir	%{GRTEBUILD}
%define _builddir	%{GRTEBUILD}/grtev%{grte_version}-runtimes
%define _rpmdir		%{_rpmtopdir}
%define _sourcedir	%{_rpmtopdir}
%define _specdir	%{_rpmtopdir}
%define _srcrpmdir	%{_rpmtopdir}
%define _build_name_fmt	%{name}-%{version}-%{release}.%{arch}.rpm
%define _unpackaged_files_terminate_build 1
%define __os_install_post %{nil}

Summary: Google Runtime Environment (GRTE) Version 1 Headers
Name: grte-headers
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-headers
AutoReqProv: no
Requires: grte-runtimes
Packager: C Compiler Team <c-compiler-team@google.com>

%description
Headers and static libraries required for compiling applications which
target GRTE.

%prep

%build

%install

%post

%files
%defattr(-,root,root)
/usr/grte/v%{grte_version}/include/*
/usr/grte/v%{grte_version}/lib/*
/usr/grte/v%{grte_version}/lib64/*

%include %{grte_changelog}
