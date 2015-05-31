%define _tmppath	%{GRTEBUILD}
%define _topdir		%{GRTEBUILD}
%define _rpmtopdir	%{GRTEBUILD}
%define _rpmdir		%{_rpmtopdir}
%define _sourcedir	%{_rpmtopdir}
%define _specdir	%{_rpmtopdir}
%define _srcrpmdir	%{_rpmtopdir}
%define _build_name_fmt	%{name}-%{version}-%{release}.%{arch}.rpm
%define _unpackaged_files_terminate_build 1
%define __os_install_post %{nil}

Summary: Google Runtime Environment (GRTE) Version 1 Headers
Name: %{grte_basename}-headers
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-headers
AutoReqProv: no
Requires: %{grte_basename}-runtime
Packager: Release Engineer <%{EMAIL}>

%description
Headers and static libraries required for compiling applications which
target GRTE.

%prep

%build

%install

%post

%files
%defattr(-,root,root)
%{grte_root}/include/*
%{grte_root}/lib/*
%{grte_root}/lib64/*

%include %{grte_changelog}
