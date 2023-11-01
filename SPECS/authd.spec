%global _hardened_build 1

Summary: A RFC 1413 ident protocol daemon
Name: authd
Version: 1.4.4
Release: 5%{?dist}.1
License: GPLv2+
URL: https://github.com/InfrastructureServices/authd
Obsoletes: pidentd < 3.2
Provides: pidentd = 3.2
Requires(post): openssl
Source0: https://github.com/InfrastructureServices/authd/releases/download/v1.4.4/authd-1.4.4.tar.gz
Source1: auth.socket
Source2: auth@.service
BuildRequires:  gcc
BuildRequires: openssl-devel gettext help2man systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

Patch0: authd-covscan.patch

%description
authd is a small and fast RFC 1413 ident protocol daemon
with both xinetd server and interactive modes that
supports IPv6 and IPv4 as well as the more popular features
of pidentd.

%prep
%autosetup

%build
make prefix=%{_prefix} CFLAGS="%{optflags}" \
        LDFLAGS="-lcrypto %{build_ldflags}"

%install
%make_install datadir=%{buildroot}/%{_datadir} \
	sbindir=%{buildroot}/%{_sbindir}

install -d %{buildroot}%{_unitdir}/
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/
install -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/

install -d %{buildroot}%{_sysconfdir}/
touch %{buildroot}%{_sysconfdir}/ident.key

install -d %{buildroot}/%{_mandir}/man1/
help2man -N -v -V %{buildroot}/%{_sbindir}/in.authd -o \
         %{buildroot}/%{_mandir}/man1/in.authd.1

%find_lang %{name}

%post
/usr/sbin/adduser -s /sbin/nologin -u 98 -r -d '/' ident 2>/dev/null || true
/usr/bin/openssl rand -base64 -out %{_sysconfdir}/ident.key 32
echo CHANGE THE LINE ABOVE TO A PASSPHRASE >> %{_sysconfdir}/ident.key
/bin/chown ident:ident %{_sysconfdir}/ident.key
chmod o-rw %{_sysconfdir}/ident.key
%systemd_post auth.socket

%postun
%systemd_postun_with_restart auth.socket

%preun
%systemd_preun auth.socket

%files -f authd.lang
%license COPYING
%verify(not md5 size mtime user group) %config(noreplace) %attr(640,root,root) %{_sysconfdir}/ident.key
%doc COPYING README.html rfc1413.txt
%{_sbindir}/in.authd
%{_mandir}/*/*
%{_unitdir}/*

%changelog
* Wed Jul 17 2019 Pavel Zhukov <pzhukov@redhat.com> - 1.4.4-5.1
- Resolves: #1722492 - Partially revert covscan fix 

* Mon Feb 18 2019 Pavel Zhukov <pzhukov@redhat.com> - 1.4.4-5
- Related: #1642073 - Properly pass hardened ld flags
- Fix covscan reported errors

* Sun Feb 17 2019 Pavel Zhukov <pzhukov@redhat.com> - 1.4.4-2
- Related: #1642073 - Rebuild with RHEL CFLAGS
- Enabled hardered build

* Tue Feb 12 2019 Pavel Zhukov <pzhukov@redhat.com> - 1.4.4-1
- Import from Fedora
- New release (v1.4.4)
- New upstream URL


