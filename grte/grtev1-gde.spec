%define _tmppath	%{GRTEBUILD}
%define _topdir		%{GRTEBUILD}
%define _rpmtopdir	%{GRTEBUILD}
%define _builddir	%{GRTEBUILD}/grtev%{grte_version}-gde
%define _rpmdir		%{_rpmtopdir}
%define _sourcedir	%{_rpmtopdir}
%define _specdir	%{_rpmtopdir}
%define _srcrpmdir	%{_rpmtopdir}
%define _build_name_fmt	%{name}-%{version}-%{release}.%{arch}.rpm
%define _unpackaged_files_terminate_build 1
%define __os_install_post %{nil}

Summary: GRTE Version %{grte_version} Development Environment (GDE to build crosstools)
Name: %{grte_basename}-gde
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-gde
AutoReqProv: no
Requires: %{grte_basename}-runtime %{grte_basename}-headers
Packager: Release Engineer <%{EMAIL}>

%description
GNU C Compiler (GCC) Version %{grte_gcc_version} and supporting files for developing
applications that use the Google Runtime Environment (GRTE). This
package includes the static versions of all of the libraries provided
in the GRTE Runtimes package, as well as the compiler itself. This also
includes all of the header files fo the standard C library, GMP and
MPFR.

%prep

%build

%install

%post

%files
%defattr(-,root,root)
%{grte_root}/etc/*
%{grte_root}/bin/*
%{grte_root}/sbin/*
%{grte_root}/include/*
%{grte_root}/lib/*
%{grte_root}/lib64/*
%{grte_root}/libexec/gcc/*
%{grte_root}/share/locale/*
%{grte_root}/share/i18n/charmaps/*
%{grte_root}/share/i18n/locales/*
%{grte_root}/x86_64-linux-gnu/*

%include %{grte_changelog}
