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

Summary: Google Runtime Environment (GRTE) Version %{grte_version} Runtimes
Name: grte-runtimes
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-runtimes
AutoReqProv: no
Packager: C Compiler Team <c-compiler-team@google.com>

%description
Basic runtime environment for all Google applications. This includes
both the 32 and 64 bit standard C library, based on glibc 2.3.6, as
well as the GCC runtime support libraries used by the GRTE Development
Environment.

%prep

%build

%install

%post
/usr/grte/v1/sbin/ldconfig

%files
%defattr(-,root,root)
%config /usr/grte/v%{grte_version}/etc/ld.so.conf
%config /usr/grte/v%{grte_version}/etc/ld.so.nohwcap
%config /usr/grte/v%{grte_version}/etc/ld.so.cache
%config /usr/grte/v%{grte_version}/lib64/gconv/gconv-modules
%config /usr/grte/v%{grte_version}/lib/gconv/gconv-modules
/usr/grte/v%{grte_version}/bin
/usr/grte/v%{grte_version}/etc/localtime
/usr/grte/v%{grte_version}/sbin
/usr/grte/v%{grte_version}/share/zoneinfo
/usr/grte/v%{grte_version}/lib/*.so*
/usr/grte/v%{grte_version}/lib/gconv/*.so*
/usr/grte/v%{grte_version}/lib/locale/locale-archive
/usr/grte/v%{grte_version}/lib64/*.so*
/usr/grte/v%{grte_version}/lib64/gconv/*.so*
/usr/grte/v%{grte_version}/lib64/locale/locale-archive
/usr/grte/v%{grte_version}/libexec/getconf
%attr(4711, root, root) /usr/grte/v%{grte_version}/libexec/pt_chown

# Short symlinks to the GRTE dynamic loader, for PT_INTERP binary editing.
/usr/grte/v%{grte_version}/ld32
/usr/grte/v%{grte_version}/ld64

%include %{grte_changelog}
