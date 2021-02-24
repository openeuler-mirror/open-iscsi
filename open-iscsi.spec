%global _hardened_build 1
%global service_enable()    /bin/systemctl enable %1.service >/dev/null 2>&1 || :
%global socket_enable()    /bin/systemctl enable %1.socket >/dev/null 2>&1 || :

Name:    open-iscsi
Version: 2.1.1
Release: 5
Summary: ISCSI software initiator daemon and utility programs
License: GPLv2+ and BSD
URL:     http://www.open-iscsi.org
Source0: https://github.com/open-iscsi/open-iscsi/archive/2.1.1.tar.gz#/open-iscsi-2.1.1.tar.gz
Patch1: 0001-change-iscsi-iqn-default-value.patch 
Patch2: 0002-iscsid-Check-nr_sessions-when-creating-a-copy-of-exi.patch
Patch3: 0003-add-sleep-for-service.patch 
Patch4: 0004-not-send-stop-message-if-iscsid-absent.patch
Patch5: 0005-iscsid-SIGTERM-syncprocess-hang.patch
Patch6: 0006-restart-log-daemon-when-exited-abnormally.patch
Patch7: 0007-check-initiator-name-out-of-range.patch
Patch8: 0008-do-not-sync-session-when-a-session-is-already-created.patch
Patch9: 0009-fix-default-file-corrupt.patch
Patch10: 0010-iscsiadm-fix-infinite-loop-while-recv-returns-0.patch
Patch11: 0011-fix-iscsiadm-logout-timeout.patch
Patch12: 0012-default-file-zero-after-power-outage.patch
Patch13: 0013-Fix-issue-where-iscsi-iname-p-core-dumps.patch 
Patch14: 0014-modify-iSCSI-shared-memory-permissions-for-logs.patch
Patch15: 0015-iscsi-Add-break-to-while-loop.patch
Patch16: 0016-iscsi-fix-fd-leak.patch
Patch17: 0017-Fix-devel-without-node-header-files.patch
Patch18: 0018-resolve-compilation-errors.patch
Patch19: 0019-Update-systemd-unit-files-for-iscsid.patch
Patch20: 0020-iscsid-Change-iscsid-service-PIDFile-to-run-iscsid.i.patch
Patch21: 0021-check-for-header-length-underflow-during-checksum-ca.patch
Patch22: 0022-check-for-u8-overflow-when-processing-TCP-options.patch
Patch23: 0023-check-for-TCP-urgent-pointer-past-end-of-frame.patch
Patch24: 0024-fix-iscsiadm-op-new-report-to-cannot-rename-error.patch

BuildRequires: flex bison doxygen kmod-devel systemd-units gcc git isns-utils-devel systemd-devel
BuildRequires: autoconf automake libtool libmount-devel openssl-devel pkg-config gdb

Provides:  iscsi-initiator-utils
Obsoletes: iscsi-initiator-utils
Provides:  iscsi-initiator-utils-iscsiuio
Obsoletes: iscsi-initiator-utils-iscsiuio
Provides:  libbopeniscsiusr
Obsoletes: libbopeniscsiusr
%{?systemd_requires}

%description
The Open-iSCSI project is a high-performance, transport independent,
multi-platform implementation of RFC3720 iSCSI.

Open-iSCSI is partitioned into user and kernel parts.

The kernel portion of Open-iSCSI is a from-scratch code
licensed under GPL. The kernel part implements iSCSI data path
(that is, iSCSI Read and iSCSI Write), and consists of three
loadable modules: scsi_transport_iscsi.ko, libiscsi.ko and iscsi_tcp.ko.

User space contains the entire control plane: configuration
manager, iSCSI Discovery, Login and Logout processing,
connection-level error processing, Nop-In and Nop-Out handling,
and (in the future:) Text processing, iSNS, SLP, Radius, etc.

The user space Open-iSCSI consists of a daemon process called
iscsid, and a management utility iscsiadm.

%package devel
Summary: Development files for %{name}
Provides: libopeniscsiusr-devel
Obsoletes: libopeniscsiusr-devel
Provides: iscsi-initiator-utils-devel
Obsoletes: iscsi-initiator-utils-devel
Requires: %{name} = %{version}-%{release}

%description devel
This package contains libraries and include files for %{name}.

%package help
Summary:  Including man files for %{name}.
Requires: man

%description help
This contains man files for the using of %{name}.

%prep
%autosetup -n open-iscsi-2.1.1 -p1
perl -i -pe 's|^exec_prefix = /$|exec_prefix = %{_exec_prefix}|' Makefile

%build
cd iscsiuio
touch AUTHORS NEWS
autoreconf --install
%{configure}
cd ..

%make_build OPTFLAGS="%{optflags} %{?__global_ldflags} -DUSE_KMOD -lkmod" LIB_DIR=%{_libdir}


%install
make DESTDIR=%{?buildroot} LIB_DIR=%{_libdir} \
     install_programs \
     install_doc \
     install_etc \
     install_iname \
     install_iface \
     install_libopeniscsiusr

install -pm 755 usr/iscsistart $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -pm 644 iscsiuio/iscsiuiolog $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/{iscsi,iscsi/nodes,iscsi/send_targets,iscsi/static,iscsi/isns,iscsi/slp,iscsi/ifaces}
install -d $RPM_BUILD_ROOT/var/lock/iscsi
touch $RPM_BUILD_ROOT/var/lock/iscsi/lock

install -d $RPM_BUILD_ROOT%{_unitdir}
install -d $RPM_BUILD_ROOT%{_libexecdir}
install -d $RPM_BUILD_ROOT%{_libdir}
install -d $RPM_BUILD_ROOT%{_includedir}
install -d $RPM_BUILD_ROOT%{_tmpfilesdir}
install -pm 644 etc/systemd/*.service $RPM_BUILD_ROOT%{_unitdir}
install -pm 644 etc/systemd/*.socket $RPM_BUILD_ROOT%{_unitdir}


%post
/sbin/ldconfig
%systemd_post iscsi.service iscsid.service iscsid.socket

if [ $1 -eq 1 ]; then
    if [ ! -f %{_sysconfdir}/iscsi/initiatorname.iscsi ]; then
        echo "InitiatorName=`%{_sbindir}/iscsi-iname`" > %{_sysconfdir}/iscsi/initiatorname.iscsi
    fi
    %service_enable iscsi
    %socket_enable  iscsid
fi

%preun
%systemd_preun iscsi.service
%systemd_preun iscsid.service iscsid.socket

%postun
/sbin/ldconfig
%systemd_postun_with_restart iscsi.service iscsid.service iscsid.socket

%files
%doc README COPYING
%dir   %{_sharedstatedir}/iscsi
%dir   %{_sharedstatedir}/iscsi/*
%ghost %{_var}/lock/iscsi
       %{_unitdir}/*
       %{_sbindir}/*
       %{_libdir}/libopeniscsiusr.so.*

%dir   %{_sysconfdir}/iscsi
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/iscsi/iscsid.conf
       %config(noreplace) %{_sysconfdir}/logrotate.d/iscsiuiolog
       %config %{_sysconfdir}/iscsi/ifaces/iface.example
%ghost %{_sysconfdir}/iscsi/initiatorname.iscsi

%files devel
       %{_includedir}/*.h
       %{_libdir}/libopeniscsiusr.so
       %{_libdir}/pkgconfig/libopeniscsiusr.pc

%files help
%{_mandir}/man8/*

%changelog
* Mon Feb 22 2021 haowenchao <haowenchao@huawei.com> - 2.1.1-5
- Fix iscsiadm op new report to can not rename error

* Mon Feb 22 2021 haowenchao <haowenchao@huawei.com> - 2.1.1-4
- Fix CVE-2020-13987 CVE-2020-13988 CVE-2020-17437

* Tue Dec 15 2020 haowenchao <haowenchao@huawei.com> - 2.1.1-3
- Change iscsid service PIDFile to /run/iscsid.ipd
  The pid file has be changed from /var/run/iscsid.pid to
  /run/iscsid.pid in code, here perform a sync.

* Tue Sep 1 2020 wuguanghao <wuguanghao3@huawei.com> - 2.1.1-2
- backport one patch for solving install problem

* Thu Jul 9 2020 wuguanghao <wuguanghao3@huawei.com> - 2.1.1-1
- update open-iscsi version to 2.1.1-1

* Sun Jul 5 2020 Zhiqiang Liu <lzhq28@mail.ustc.edu.cn> - 2.0.876-22
- remove useless readme files

* Mon Jun 15 2020 sunguoshuai <sunguoshuai@huawei.com> - 2.0.876-21
- fix devel without node header files

* Mon Jun 15 2020 Zhiqiang Liu <liuzhiqiang26@huawei.com> - 2.0.876-20
- Backport two upstream bugfix patches

* Tue May 12 2020 Wu Bo <wubo@huawei.com> - 2.0.876-19
- iscsi-iname verfiy prefix length is at most 210 characters.
  iscsi-iname remove unneeded temp buffer.
  Fix issuse where 'iscsi-iname -p' core dumps.
  modify iSCSI shared memory permissions for log.

* Sat Mar 21 2020 sunguoshuai <sunguoshuai@huawei.com> - 2.0.876-18
- Fix upgrade problem and add gdb buildrequire.

* Tue Jan 21 2020 geruijun <geruijun@huawei.com> - 2.0.876-17
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:remove iscsiuio service

* Mon Jan 20 2020 geruijun <geruijun@huawei.com> - 2.0.876-16
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:fix service error

* Fri Jan 17 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-15
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:fix install error

* Sat Jan 11 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-14
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:provide iscsi-initiator-utils-devel

* Thu Jan 9 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-13
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:update package

* Tue Dec 31 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-12
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:use openEuler version to match RPM package version

* Mon Dec 30 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-11
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:change iscsi iqn default value

* Sun Dec 29 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-10
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:do not display the fail info while uninstalling

* Mon Dec 23 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-9
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:backport patches for fix bug

* Tue Oct 29 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-8
- Add %systemd_postun parameter.

* Fri Sep 20 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-7
- Package init
