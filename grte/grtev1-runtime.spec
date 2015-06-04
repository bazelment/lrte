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

Summary: Linux C/C++ Runtime Environment (LRTE) Version %{grte_version} Runtimes
Name: %{grte_basename}-runtime
Version: %{grte_rpmver}
Release: %{grte_rpmrel}
License: GPL
Group: Development/Debuggers
BuildRoot: %{_tmppath}/grtev%{grte_version}-runtime
AutoReqProv: no
Packager: Release Engineer <%{maintainer_email}>

%description
Basic runtime environment for all portable Linux C/C++ applications. This includes
both the 32 and 64 bit standard C library, based on glibc %{grte_glibc_version}, as
well as the GCC runtime support libraries used by the LRTE Development
Environment.


%prep

%build

%install

%post
%{grte_root}/sbin/ldconfig 2>/dev/null

%files
%defattr(-,root,root)
%config %{grte_root}/etc/ld.so.conf
%config %{grte_root}/etc/ld.so.nohwcap
%config %{grte_root}/etc/ld.so.cache
%config %{grte_root}/lib64/gconv/gconv-modules
%{grte_root}/bin
%{grte_root}/etc/localtime
%{grte_root}/sbin
%{grte_root}/share/zoneinfo
%{grte_root}/lib64/*.so*
%{grte_root}/lib64/gconv/*.so*
%{grte_root}/lib64/locale/locale-archive
%{grte_root}/libexec/getconf
%{grte_root}/share/gcc-*/python/*
# Short symlinks to the LRTE dynamic loader, for PT_INTERP binary editing.
%{grte_root}/ld32
%{grte_root}/ld64

%include %{grte_changelog}
