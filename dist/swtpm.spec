%bcond_without gnutls

%global gitdate     20201007
%global gitcommit   enter_commit_here
%global gitshortcommit  %(c=%{gitcommit}; echo ${c:0:7})

# Macros needed by SELinux
%global selinuxtype targeted
%global moduletype  contrib
%global modulename  swtpm

Summary: TPM Emulator
Name:           swtpm
Version:        0.6.0
Release:        0.%{gitdate}git%{gitshortcommit}%{?dist}
License:        BSD
Url:            http://github.com/stefanberger/swtpm
Source0:        %{url}/archive/%{gitcommit}/%{name}-%{gitshortcommit}.tar.gz

BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  libtpms-devel >= 0.6.0
BuildRequires:  glib2-devel
BuildRequires:  json-glib-devel
BuildRequires:  gmp-devel
BuildRequires:  expect
BuildRequires:  net-tools
BuildRequires:  openssl-devel
BuildRequires:  socat
BuildRequires:  python3-twisted
BuildRequires:  softhsm
BuildRequires:  trousers >= 0.3.9
%if %{with gnutls}
BuildRequires:  gnutls >= 3.1.0
BuildRequires:  gnutls-devel
BuildRequires:  gnutls-utils
BuildRequires:  libtasn1-devel
BuildRequires:  libtasn1
%endif
BuildRequires:  selinux-policy-devel
BuildRequires:  gcc
BuildRequires:  libseccomp-devel
BuildRequires:  tpm2-pkcs11 tpm2-pkcs11-tools tpm2-tools tpm2-abrmd

Requires:       %{name}-libs = %{version}-%{release}
Requires:       libtpms >= 0.6.0
%{?selinux_requires}

%description
TPM emulator built on libtpms providing TPM functionality for QEMU VMs

%package        libs
Summary:        Private libraries for swtpm TPM emulators
License:        BSD

%description    libs
A private library with callback functions for libtpms based swtpm TPM emulator

%package        devel
Summary:        Include files for the TPM emulator's CUSE interface for usage by clients
License:        BSD
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description    devel
Include files for the TPM emulator's CUSE interface.

%package        tools
Summary:        Tools for the TPM emulator
License:        BSD
Requires:       swtpm = %{version}-%{release}
Requires:       trousers >= 0.3.9 bash gnutls-utils python3 python3-cryptography

%description    tools
Tools for the TPM emulator from the swtpm package

%package       tools-pkcs11
Summary:       Tools for creating a local CA based on a pkcs11 device
License:       BSD
Requires:      swtpm-tools = %{version}-%{release}
Requires:      tpm2-pkcs11 tpm2-pkcs11-tools tpm2-tools tpm2-abrmd
Requires:      expect gnutls-utils trousers >= 0.3.9

%description   tools-pkcs11
Tools for creating a local CA based on a pkcs11 device

%prep
%autosetup -n %{name}-%{gitcommit}

%build

NOCONFIGURE=1 ./autogen.sh
%configure \
%if %{with gnutls}
        --with-gnutls \
%endif
        --without-cuse

%make_build

%check
make %{?_smp_mflags} check

%install

%make_install
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/*.{a,la,so}

%post
for pp in /usr/share/selinux/packages/swtpm.pp \
          /usr/share/selinux/packages/swtpm_svirt.pp; do
  %selinux_modules_install -s %{selinuxtype} ${pp}
done

%postun
if [ $1 -eq  0 ]; then
  for p in swtpm swtpm_svirt; do
    %selinux_modules_uninstall -s %{selinuxtype} $p
  done
fi

%posttrans
%selinux_relabel_post -s %{selinuxtype}

%ldconfig_post libs
%ldconfig_postun libs

%files
%license LICENSE
%doc README
%{_bindir}/swtpm
%{_mandir}/man8/swtpm.8*
%{_datadir}/selinux/packages/swtpm.pp
%{_datadir}/selinux/packages/swtpm_svirt.pp

%files libs
%license LICENSE
%doc README

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libswtpm_libtpms.so.0
%{_libdir}/%{name}/libswtpm_libtpms.so.0.0.0

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_mandir}/man3/swtpm_ioctls.3*

%files tools
%doc README
%{_bindir}/swtpm_bios
%if %{with gnutls}
%{_bindir}/swtpm_cert
%endif
%{_bindir}/swtpm_setup
%{_bindir}/swtpm_ioctl
%{_mandir}/man8/swtpm_bios.8*
%{_mandir}/man8/swtpm_cert.8*
%{_mandir}/man8/swtpm_ioctl.8*
%{_mandir}/man8/swtpm-localca.conf.8*
%{_mandir}/man8/swtpm-localca.options.8*
%{_mandir}/man8/swtpm-localca.8*
%{_mandir}/man8/swtpm_setup.8*
%{_mandir}/man8/swtpm_setup.conf.8*
%{_mandir}/man8/swtpm_setup.sh.8*
%config(noreplace) %{_sysconfdir}/swtpm_setup.conf
%config(noreplace) %{_sysconfdir}/swtpm-localca.options
%config(noreplace) %{_sysconfdir}/swtpm-localca.conf
%dir %{_datadir}/swtpm
%{_datadir}/swtpm/swtpm-localca
%{_datadir}/swtpm/swtpm-create-user-config-files
%{python3_sitelib}/py_swtpm_setup/*
%{python3_sitelib}/swtpm_setup-*/*
%{python3_sitelib}/py_swtpm_localca/*
%{python3_sitelib}/swtpm_localca-*/*
%attr( 750, tss, root) %{_localstatedir}/lib/swtpm-localca

%files tools-pkcs11
%{_mandir}/man8/swtpm-create-tpmca.8*
%{_datadir}/swtpm/swtpm-create-tpmca

%changelog
* Wed Oct 7 2020 Stefan Berger <stefanb@linux.ibm.com> - 0.5.0-0.20201007git-------
- v0.5.0 release

* Fri Aug 28 2020 Stefan Berger <stefanb@linux.ibm.com> - 0.4.0-20200218git-------
- v0.4.0 release

* Mon Feb 17 2020 Stefan Berger <stefanb@linux.ibm.com> - 0.3.0-20200218git38f36f3
- v0.3.0 release

* Fri Jul 19 2019 Stefan Berger <stefanb@linux.ibm.com> - 0.2.0-20190716git817d3a8
- v0.2.0 release

* Mon Feb 4 2019 Stefan Berger <stefanb@linux.vnet.ibm.com> - 0.1.0-0.20190204git2c25d13
- v0.1.0 release

* Mon Sep 17 2018 Stefan Berger <stefanb@linux.vnet.ibm.com> - 0.1.0-0.20180918git67d7ea3
- Created initial version of rpm spec files
- Version is now 0.1.0
- Bugzilla for this spec: https://bugzilla.redhat.com/show_bug.cgi?id=1611829
