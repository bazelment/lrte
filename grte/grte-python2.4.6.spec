#
# Python2.4.6 base spec file
# $Id: //depot/google_vendor_src_branch/python/grte-python2.4.6.spec#1 $
#

# This file should be kept in sync with the grte-python2.4-2.4.6-debian-*
# files.

%define include_tkinter 0

%define name grte-python

# major package version (ie. grte-python2.2, 2.3, etc.)
%define rel_ver 2.4
%define binsuffix %{rel_ver}
# python.org code release
%define version 2.4.6
# google release version (tracks internal changes)
%define release 7

%define __prefix /usr/grte/v1
%define __debugdir /usr/lib/debug

# Should unpackaged files in a build root terminate a build?  
#
# Yes: The Python build script ignores errors when building extension
# modules, meaning that we may be missing arbitrary modules.
# Therefore we have a complete manifest of shared libraries below, and
# set these variables to enforce that manifest.
%define _unpackaged_files_terminate_build 1
%define _missing_doc_files_terminate_build 1

Summary: A high-level object-oriented programming language.
Name: %{name}%{binsuffix}
Version: %{version}
Release: %{release}
License: Python Software Foundation License Version 2
Group: Development/Languages
Source: Python-%{version}.tgz
Prefix: %{__prefix}
Packager: Thomas Wouters <twouters@google.com>
AutoProv: no
AutoReqProv: no
Requires: grte-runtimes >= 1.0

%description
Python package for the Google Runtime Environment (GRTE).

$Id: //depot/google_vendor_src_branch/python/grte-python2.4.6.spec#1 $

%package devel
Summary: The libraries and header files needed for Python extension development.
Group: Development/Libraries
AutoProv: no
AutoReqProv: no
Requires: %{name} = %{version}

%description devel
Python 'devel' package for the Google Runtime Environment (GRTE).
The 'devel' package holds files necessary to compile extensions
against this Python version, using distutils. It also holds the debug
symbols of shared libraries.

$Id: //depot/google_vendor_src_branch/python/grte-python2.4.6.spec#1 $

%package test
Summary: Self-tests for the Python scripting language.
Group: Development/Languages
AutoProv: no
AutoReqProv: no
Requires: %{name} = %{version}

%description test
Self-tests of the Python package for the Google Runtime Environment (GRTE).

$Id: //depot/google_vendor_src_branch/python/grte-python2.4.6.spec#1 $

%package tkinter
Summary: Do not install or use this package
Group: Development/Library
AutoProv: no
AutoReqProv: no
Requires: %{name} = %{version}

%description tkinter
This package doesn't work due to lack of Tk libraries on prod71
machines.  Do not use.

$Id: //depot/google_vendor_src_branch/python/grte-python2.4.6.spec#1 $

%prep

# Sources are already unpacked in Perforce

%build

# Build is done by setup-grte-python246.sh

%install

# Install is done by setup-grte-python246.sh

%clean

# No thanks

%files
%defattr(-,root,root,-)

%{__prefix}/piii-linux/bin/python%{rel_ver}

%{__prefix}/piii-linux/lib/python%{rel_ver}/*.doc
%{__prefix}/piii-linux/lib/python%{rel_ver}/*.py*
%{__prefix}/piii-linux/lib/python%{rel_ver}/*.txt
%{__prefix}/piii-linux/lib/python%{rel_ver}/bsddb/*.py*
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/bsddb/test
%{__prefix}/piii-linux/lib/python%{rel_ver}/compiler
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/config
%{__prefix}/piii-linux/lib/python%{rel_ver}/curses
%{__prefix}/piii-linux/lib/python%{rel_ver}/email/*.py*
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/email/test
%{__prefix}/piii-linux/lib/python%{rel_ver}/encodings
%{__prefix}/piii-linux/lib/python%{rel_ver}/hotshot
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/idlelib
# listed below %{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-old
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/lib-tk
%{__prefix}/piii-linux/lib/python%{rel_ver}/logging
%{__prefix}/piii-linux/lib/python%{rel_ver}/plat-linux2
%{__prefix}/piii-linux/lib/python%{rel_ver}/site-packages
%{__prefix}/piii-linux/lib/python%{rel_ver}/xml

# All extension modules are individually listed to ensure that they
# all were successfully built.
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/array.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/audioop.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/binascii.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_bisect.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_bsddb.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/bz2.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/cmath.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_cn.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_hk.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_iso2022.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_jp.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_kr.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_codecs_tw.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/collections.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/cPickle.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/crypt.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/cStringIO.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_csv.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_curses_panel.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_curses.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/datetime.so
# GRTE's GDBM doesn't provide NDBM support, so dbm.so does not work
# exclude %{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/dbm.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/dl.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/fcntl.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/gdbm.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/grp.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_heapq.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_hotshot.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/imageop.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/itertools.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/linuxaudiodev.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_locale.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/math.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/md5.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/mmap.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_multibytecodec.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/nis.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/operator.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/ossaudiodev.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/parser.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/pyexpat.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_random.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/readline.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/regex.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/resource.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/rgbimg.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/select.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/sha.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_socket.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_ssl.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/strop.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/struct.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/syslog.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/termios.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/time.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/timing.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/unicodedata.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_weakref.so
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/zlib.so

%{__prefix}/k8-linux/bin/python%{rel_ver}

%{__prefix}/k8-linux/lib/python%{rel_ver}/*.doc
%{__prefix}/k8-linux/lib/python%{rel_ver}/*.py*
%{__prefix}/k8-linux/lib/python%{rel_ver}/*.txt
%{__prefix}/k8-linux/lib/python%{rel_ver}/bsddb/*.py*
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/bsddb/test
%{__prefix}/k8-linux/lib/python%{rel_ver}/compiler
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/config
%{__prefix}/k8-linux/lib/python%{rel_ver}/curses
%{__prefix}/k8-linux/lib/python%{rel_ver}/email/*.py*
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/email/test
%{__prefix}/k8-linux/lib/python%{rel_ver}/encodings
%{__prefix}/k8-linux/lib/python%{rel_ver}/hotshot
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/idlelib
# listed below %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-old
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-tk
%{__prefix}/k8-linux/lib/python%{rel_ver}/logging
%{__prefix}/k8-linux/lib/python%{rel_ver}/plat-linux2
%{__prefix}/k8-linux/lib/python%{rel_ver}/site-packages
%{__prefix}/k8-linux/lib/python%{rel_ver}/xml

# All extension modules are individually listed to ensure that they
# all were successfully built.
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/array.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/audioop.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/binascii.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_bisect.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_bsddb.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/bz2.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/cmath.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_cn.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_hk.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_iso2022.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_jp.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_kr.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_codecs_tw.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/collections.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/cPickle.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/crypt.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/cStringIO.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_csv.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_curses_panel.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_curses.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/datetime.so
# GRTE's GDBM doesn't provide NDBM support, so dbm.so does not work
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/dbm.so
# dl.so doesn't work in 64-bit builds
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/dl.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/fcntl.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/gdbm.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/grp.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_heapq.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_hotshot.so
# imageop.so doesn't work in 64-bit builds
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/imageop.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/itertools.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/linuxaudiodev.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_locale.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/math.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/md5.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/mmap.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_multibytecodec.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/nis.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/operator.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/ossaudiodev.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/parser.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/pyexpat.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_random.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/readline.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/regex.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/resource.so
# rgbimg.so doesn't work in 64-bit builds
# exclude %{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/rgbimg.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/select.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/sha.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_socket.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_ssl.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/strop.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/struct.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/syslog.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/termios.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/time.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/timing.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/unicodedata.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_weakref.so
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/zlib.so

%files devel
%defattr(-,root,root,-)

%{__prefix}/piii-linux/bin/idle2.4
%{__prefix}/piii-linux/bin/pydoc2.4
%{__prefix}/piii-linux/include
%{__prefix}/piii-linux/lib/python%{rel_ver}/config
%{__prefix}/piii-linux/lib/python%{rel_ver}/idlelib
%{__prefix}/piii-linux/lib/python%{rel_ver}/distutils
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_testcapi.so
%{__debugdir}%{__prefix}/piii-linux/bin/python%{rel_ver}
%{__debugdir}%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/*.so

%{__prefix}/k8-linux/bin/idle2.4
%{__prefix}/k8-linux/bin/pydoc2.4
%{__prefix}/k8-linux/include
%{__prefix}/k8-linux/lib/python%{rel_ver}/config
%{__prefix}/k8-linux/lib/python%{rel_ver}/idlelib
%{__prefix}/k8-linux/lib/python%{rel_ver}/distutils
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_testcapi.so
%{__debugdir}%{__prefix}/k8-linux/bin/python%{rel_ver}
%{__debugdir}%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/*.so

%files test
%defattr(-,root,root,-)

%{__prefix}/piii-linux/lib/python%{rel_ver}/test
%{__prefix}/piii-linux/lib/python%{rel_ver}/bsddb/test
%{__prefix}/piii-linux/lib/python%{rel_ver}/email/test

%{__prefix}/k8-linux/lib/python%{rel_ver}/test
%{__prefix}/k8-linux/lib/python%{rel_ver}/bsddb/test
%{__prefix}/k8-linux/lib/python%{rel_ver}/email/test

# The tkinter package is unusable, but we build it anyway to shut up
# rpmbuild warnings about unused files in the build root.
%files tkinter
%defattr(-,root,root)

%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-tk
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-tk
%if %{include_tkinter}
%{__prefix}/piii-linux/lib/python%{rel_ver}/lib-dynload/_tkinter.so*
%{__prefix}/k8-linux/lib/python%{rel_ver}/lib-dynload/_tkinter.so*
%endif

%changelog
* Mon Nov 23 2009 Thomas Wouters <twouters@google.com> 2.4.6-7
- Depend on grte-runtimes 1.0-or-later instead of just 1.0.

* Thu Nov 19 2009 Thomas Wouters <twouters@google.com> 2.4.6-6
- Work around a potential but improbable backward compatibility issue
  when embedding Python in grte-python2.4-2.4.6-5.

* Tue Nov 12 2009 Thomas Wouters <twouters@google.com> 2.4.6-5
- Backport upstream r60097, fixing some pathologically bad performance
  in the subprocess module.

* Fri Oct 30 2009 Thomas Wouters <twouters@google.com> 2.4.6-4
- Build the 64-bit library using -fPIC, allowing static linking.

* Fri Sep 11 2009 Thomas Wouters <twouters@google.com> 2.4.6-3
- Fix incorrect detection of availability of -fwrapv, causing a build
  without it.

* Wed Sep 9 2009 Thomas Wouters <twouters@google.com> 2.4.6-2
- Fix http://b/1769064, incorrect encoding aliases for UTF-8.
- Fix http://b/1943315, a deadlock when mixing threads and fork().
- Properly pass -fwrapv to gcc while building.
- Fix potential issues with the mmap module in 64-bit builds.

* Wed Jan 14 2009 Thomas Wouters <twouters@google.com> 2.4.6-1
- Update to upstream version 2.4.6.

* Mon Sep 15 2008 Thomas Wouters <twouters@google.com> 2.4.5-8
- Change build script to keep as many files as possible identical
  and with the same timestamps as the last RPM pushed to prod71.
- Use relative instead of absolute symlinks for the .py symlinks
  from piii-linux to k8-linux.

* Mon Jul 28 2008 Thomas Wouters <twouters@google.com> 2.4.5-7
- Fix detection of readline > 4.0 by explicitly linking against termcap
  from /usr/lib.
- Fix IPv6 support in socket.getaddrinfo()
- Backport upstream r65481, preventing another infinite loop in
  impossible situations.

* Mon May 12 2008 Thomas Wouters <twouters@google.com> 2.4.5-6
- Dump debug symbols in /usr/lib/debug and package them in the
  devel package.

* Mon Mar 31 2008 Thomas Wouters <twouters@google.com> 2.4.5-5
- Strip just debug symbols from /usr/bin/python2.4, not all symbols,
  and recompile the .pyc files after modifying the .py files so the
  timestamps are correct.

* Tue Mar 25 2008 Thomas Wouters <twouters@google.com> 2.4.5-4
- Make a few identical ancillary files symlinks.

* Mon Mar 24 2008 Thomas Wouters <twouters@google.com> 2.4.5-3
- Rebuild with --with-cxx=no to avoid linking with g++ and introducing
  a dependency on libstdc++.so.6.

* Fri Mar 21 2008 Thomas Wouters <twouters@google.com> 2.4.5-2
- Backport upstream r60148, preventing an infinite loop deep in
  thread-switching mechanics (aborting instead.)

* Wed Feb 13 2008 Thomas Wouters <twouters@google.com> 2.4.5-1
- Initial build.
