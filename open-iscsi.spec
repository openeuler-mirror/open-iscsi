%global _hardened_build 1
%global service_enable()    /bin/systemctl enable %1.service >/dev/null 2>&1 || :
%global socket_enable()    /bin/systemctl enable %1.socket >/dev/null 2>&1 || :

Name:    open-iscsi
Version: 2.1.5
Release: 13
Summary: ISCSI software initiator daemon and utility programs
License: GPLv2+ and BSD
URL:     http://www.open-iscsi.com
Source0: https://github.com/open-iscsi/open-iscsi/archive/2.1.5.tar.gz#/open-iscsi-2.1.5.tar.gz
patch1: 0001-change-iscsi-iqn-default-value.patch
patch2: 0002-iscsid-Check-nr_sessions-when-creating-a-copy-of-exi.patch
patch3: 0003-restart-log-daemon-when-exited-abnormally.patch
patch4: 0004-check-initiator-name-out-of-range.patch
patch5: 0005-iscsid-Check-session-id-before-start-sync-a-thread.patch
patch6: 0006-fix-default-file-corrupt.patch
patch7: 0007-fix-iscsiadm-logout-timeout.patch
patch8: 0008-default-file-zero-after-power-outage.patch
patch9: 0009-fix-iscsiadm-op-new-report-to-cannot-rename-error.patch
patch10: 0010-Fix-compiler-error-introduced-with-recent-IPv6-commi.patch
patch11: 0011-Remove-iscsid.service-s-dependence-of-iscsi-init.ser.patch
patch12: 0012-Remove-session-info-password-print.patch
patch13: 0013-Remove-iscsiuio-from-build-and-install-recipe.patch
patch14: 0014-Remove-iscsiuio-source-code.patch
patch15: 0015-Remove-iscsiuio-from-config-and-service-file.patch
patch16: 0016-Remove-iscsi-init.service-from-iscsi-and-iscsid-serv.patch
patch17: 0017-iscsi-sysfs-check-state-before-onlining-devs.patch
patch18: 0018-iscsiadm-Call-log_init-first-to-fix-a-segmentation-f.patch
patch19: 0019-Fix-issues-discovered-by-gcc12.patch
patch20: 0020-Fix-more-issues-discovered-by-gcc12.patch
patch21: 0021-actor-enhanced-print-error-log-when-init-a-initilize.patch
patch22: 0022-initiator_common-make-set-operational-parameter-log-.patch
patch23: 0023-Remove-unused-fwparam_ibft.-ch-files-in-fwparam_ibft.patch
patch24: 0024-Fix-a-possible-passing-null-pointer-in-usr-iface.c-3.patch
patch25: 0025-iscsid-iscsiuio-fix-OOM-adjustment-377.patch
patch26: 0026-iscsid-clear-scanning-thread-s-PR_SET_IO_FLUSHER-fla.patch
patch27: 0027-iscsid-stop-connection-for-recovery-if-error-is-not-.patch
patch28: 0028-discoveryd-fix-format-overflow-warning-413.patch

BuildRequires: flex bison doxygen kmod-devel systemd-units gcc git isns-utils-devel systemd-devel
BuildRequires: autoconf automake libtool libmount-devel openssl-devel pkg-config

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
%autosetup -n %{name}-%{version} -p1
perl -i -pe 's|^exec_prefix = /$|exec_prefix = %{_exec_prefix}|' Makefile

%build
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
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{iscsi,iscsi/nodes,iscsi/send_targets,iscsi/static,iscsi/isns,iscsi/slp,iscsi/ifaces}
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
%dir   %{_sysconfdir}/iscsi
%dir   %{_sysconfdir}/iscsi/*
%ghost %{_var}/lock/iscsi
       %{_unitdir}/*
       %{_sbindir}/*
       %{_libdir}/libopeniscsiusr.so.*
%exclude %{_unitdir}/iscsi-init.service


%dir   %{_sysconfdir}/iscsi
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/iscsi/iscsid.conf
       %config %{_sysconfdir}/iscsi/ifaces/iface.example
%ghost %{_sysconfdir}/iscsi/initiatorname.iscsi

%files devel
       %{_includedir}/*.h
       %{_libdir}/libopeniscsiusr.so
       %{_libdir}/pkgconfig/libopeniscsiusr.pc

%files help
%{_mandir}/man8/*

%changelog
* Sun Jun 25 2023 louhongxiang <louhongxiang@huawei.com> - 2.1.5-13
- iscsid: fix format overflow warning.

* Tue Jan 17 2023 haowenchao <haowenchao@huawei.com> - 2.1.5-12
- iscsid: stop connection for recovery if error is not timeout in iscsi_login_eh

* Tue Jan 17 2023 haowenchao <haowenchao@huawei.com> - 2.1.5-11
- iscsid: clear scanning thread's PR_SET_IO_FLUSHER flag

* Fri Dec 2 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-10
- Backport bugfix patches from mainline

* Tue Sep 27 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-9
- Substitute self-developed patch with mainline patch

* Thu Jun 23 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-8
- Remove unused fwparam_ibft.[ch] files in fwparam_ibft

* Fri Feb 18 2022 wubo <wubo40@huawei.com> - 2.1.5-7
- Backport bugfix patches

* Tue Feb 8 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-6
- Remove useless patch

* Tue Feb 8 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-5
- Remove iscsi's dependence of iscsid-init.service

* Wed Jan 26 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-4
- Remove tool iscsiuio

* Tue Jan 25 2022 haowenchao <haowenchao@huawei.com> - 2.1.5-3
- Remove password print in session info display

* Mon Dec 6 2021 haowenchao <haowenchao@huawei.com> - 2.1.5-2
- Remove iscsid's dependence of iscsid-init.service

* Tue Nov 16 2021 haowenchao <haowenchao@huawei.com> - 2.1.5-1
- Update open-iscsi version to 2.1.5-1

* Thu Oct 21 2021 haowenchao <haowenchao@huawei.com> - 2.1.3-6
- update upstream URL

* Fri Jul 23 2021 zhouwenpei <zhouwenpei1@huawei.com> - 2.1.3-5
- remove unnecessary build require.

* Thu Apr 8 2021 haowenchao <haowenchao@huawei.com> - 2.1.3-4
- Fix file residual files after open-iscsi removed

* Mon Mar 1 2021 haowenchao <haowenchao@huawei.com> - 2.1.3-3
- Fix iscsiadm segfault when exiting

* Mon Feb 22 2021 haowenchao <haowenchao@huawei.com> - 2.1.3-2
- Fix iscsiadm op new report to can not rename error

* Thu Jan 28 2021 haowenchao <haowenchao@huawei.com> - 2.1.3-1
- Update open-iscsi version to 2.1.3-1

* Sat Dec 12 2020 haowenchao <haowenchao@huawei.com> - 2.1.1-5
- Change iscsid service PIDFile to /run/iscsid.ipd
  The pid file has be changed from /var/run/iscsid.pid to
  /run/iscsid.pid in code, here perform a sync.

* Thu Nov 12 2020 haowenchao <haowenchao@huawei.com> - 2.1.1-4
- backport patches from epoch2 including following changes:
  get_random_bytes is replaced by RAND_bytes so it is removed
  fix buffer overflow when discovering

* Sat Oct 31 2020 haowenchao <haowenchao@huawei.com> - 2.1.1-3
- backport patches from epoch1

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
