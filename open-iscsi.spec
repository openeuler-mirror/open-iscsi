%global _hardened_build 1
%global service_enable()    /bin/systemctl enable %1.service >/dev/null 2>&1 || :
%global socket_enable()    /bin/systemctl enable %1.socket >/dev/null 2>&1 || :

Name:    open-iscsi
Version: 2.0.876
Release: 13
Summary: ISCSI software initiator daemon and utility programs
License: GPLv2+ and BSD
URL:     http://www.open-iscsi.org
Source0: https://github.com/open-iscsi/open-iscsi/archive/f3c8e90fc0894c088950a15ee6618b427f9e2457.tar.gz#/open-iscsi-f3c8e90.tar.gz

Patch6000: 6000-Plugging-a-memory-leak-from-discovery.patch
Patch6001: 6001-Fix-bug-in-error-message-when-reading-sysfs-numbers.patch
Patch6002: 6002-Do-not-allow-multiple-sessions-when-nr_sessions-1.patch
Patch6003: 6003-Fix-possible-discovery-hang-when-timing-out.patch
Patch6004: 6004-Resource-leak-returning-without-freeing-netdev.patch
Patch6005: 6005-Out-of-bounds-write-Overrunning-array-link_target.patch
Patch6006: 6006-Resource-leak-Variable-rec-going-out-of-scope-leaks.patch
Patch6007: 6007-Out-of-bounds-write-Overrunning-array-link_target.patch
Patch6008: 6008-Buffer-not-null-terminated-Calling-strncpy.patch
Patch6009: 6009-Resource-leak-Variable-startup_cmd-going-out-of-scop.patch
Patch6010: 6010-Buffer-not-null-terminated-Calling-strncpy.patch
Patch6011: 6011-Uninitialized-scalar-variable.patch
Patch6012: 6012-Resource-leak-Handle-variable-sockfd-going-out-of-scope.patch
Patch6013: 6013-Resource-leak-Variable-chap_info-going-out-of-scope.patch
Patch6014: 6014-Resource-leak-Variable-matched_ses-going-out-of-scope.patch
Patch6015: 6015-Resource-leak-Handle-variable-fd-going-out-of-scope.patch
Patch6016: 6016-Resource-leak-Handle-variable-fd-going-out-of-scope.patch
Patch6017: 6017-Out-of-bounds-read.patch
Patch6018: 6018-fwparam_pcc-mulitple-resource-leaks.patch
Patch6019: 6019-Resource-leak-Handl-variable-fd.patch
Patch6020: 6020-Resource-leak-Variable-raw.patch
Patch6021: 6021-Allow-reading-sysfs-port-to-fail-gracefully.patch
Patch6022: 6022-Fix-incorrect-sysfs-logic-for-port-and-ip-address.patch
Patch6023: 6023-Handle-ENOTCONN-error-separately-when-reading-sysfs.patch
Patch6024: 6024-update-service-files.patch

Patch9000: 9000-change-iscsi-iqn-default-value.patch
Patch9001: 9001-iscsid-Check-nr_sessions-when-creating-a-copy-of-exi.patch
Patch9002: 9002-add-sleep-for-service.patch
Patch9003: 9003-not-send-stop-message-if-iscsid-absent.patch
Patch9004: 9004-iscsid-SIGTERM-syncprocess-hang.patch
Patch9005: 9005-fix-timeout-setting-on-session-commands.patch
Patch9006: 9006-restart-log-daemon-when-exited-abnormally.patch
Patch9007: 9007-check-initiator-name-out-of-range.patch
Patch9008: 9008-do-not-sync-session-when-a-session-is-already-created.patch
Patch9009: 9009-fix-default-file-corrupt.patch
Patch9010: 9010-iscsiadm-fix-infinite-loop-while-recv-returns-0.patch
Patch9011: 9011-fix-iscsiadm-logout-timeout.patch
Patch9012: 9012-default-file-zero-after-power-outage.patch
Patch9013: 9013-modify-utils-iscsi-iname.patch
Patch9014: 9014-iscsi-iname-p-name-occur-buffer-overflow.patch

BuildRequires: flex bison doxygen kmod-devel systemd-units gcc git isns-utils-devel
BuildRequires: autoconf automake libtool libmount-devel openssl-devel pkg-config

Provides:  iscsi-initiator-utils
Obsoletes: iscsi-initiator-utils
Provides:  iscsi-initiator-utils-iscsiuio
Obsoletes: iscsi-initiator-utils-iscsiuio
Provides:  libbopeniscsiusr
Obsoletes: libbopeniscsiusr
Obsoletes: %{name}-devel < %{version}-%{release}
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
Requires: %{name} = %{version}-%{release}

%description devel
This package contains libraries and include files for %{name}.

%package help
Summary:  Including man files for %{name}.
Requires: man

%description help
This contains man files for the using of %{name}.

%prep
%autosetup -n open-iscsi-f3c8e90fc0894c088950a15ee6618b427f9e2457 -p1
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
%systemd_post iscsi.service iscsi-shutdown.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket

if [ $1 -eq 1 ]; then
    if [ ! -f %{_sysconfdir}/iscsi/initiatorname.iscsi ]; then
        echo "InitiatorName=`%{_sbindir}/iscsi-iname`" > %{_sysconfdir}/iscsi/initiatorname.iscsi
    fi
    %service_enable iscsi
    %socket_enable  iscsid
fi

%preun
%systemd_preun iscsi.service
%systemd_preun iscsi-shutdown.service >/dev/null 2>&1
%systemd_preun iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket

%postun
/sbin/ldconfig
%systemd_postun iscsi.service iscsi-shutdown.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket

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
* Wed Jan 9 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.0.876-13
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
