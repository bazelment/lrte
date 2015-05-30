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
Name: grte-debuginfo
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-debuginfo
AutoReqProv: no
Packager: C Compiler Team <c-compiler-team@google.com>

%description
Debug symbols for the libaries in the grte-runtimes package.

%prep

%build

%install

%post

%files
%defattr(-,root,root)
/usr/grte/v%{grte_version}/bin/.debug
/usr/grte/v%{grte_version}/debug-src
/usr/grte/v%{grte_version}/lib/.debug
/usr/grte/v%{grte_version}/lib/gconv/.debug
/usr/grte/v%{grte_version}/lib64/.debug
/usr/grte/v%{grte_version}/lib64/gconv/.debug
/usr/grte/v%{grte_version}/libexec/.debug
/usr/grte/v%{grte_version}/libexec/gcc/x86_64-linux-gnu/4.2.2/.debug
/usr/grte/v%{grte_version}/libexec/gcc/x86_64-linux-gnu/4.2.2/install-tools/.debug
/usr/grte/v%{grte_version}/sbin/.debug
/usr/grte/v%{grte_version}/x86_64-linux-gnu/bin/.debug

%include %{grte_changelog}
