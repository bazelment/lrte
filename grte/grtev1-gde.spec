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

Summary: GRTE Version %{grte_version} Development Environment (GDE)
Name: grte-gde
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-gde
AutoReqProv: no
Requires: grte-runtimes grte-headers
Packager: C Compiler Team <c-compiler-team@google.com>

%description
GNU C Compiler (GCC) Version 4.2.2 and supporting files for developing
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
/usr/grte/v%{grte_version}/etc/*
/usr/grte/v%{grte_version}/bin/*
/usr/grte/v%{grte_version}/sbin/*
/usr/grte/v%{grte_version}/include/*
/usr/grte/v%{grte_version}/lib/*
/usr/grte/v%{grte_version}/lib64/*
/usr/grte/v%{grte_version}/libexec/gcc/*
/usr/grte/v%{grte_version}/share/locale/*
/usr/grte/v%{grte_version}/share/i18n/charmaps/*
/usr/grte/v%{grte_version}/share/i18n/locales/*
/usr/grte/v%{grte_version}/x86_64-linux-gnu/*

%include %{grte_changelog}
