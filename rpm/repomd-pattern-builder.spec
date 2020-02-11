Name:       repomd-pattern-builder
Summary:    Scripts to build patterns for the rpm repository
Version:    0.3
Release:    1
License:    GPLv2+
URL:        https://git.sailfishos.org/mer-core/repomd-pattern-builder
Source0:    %{name}-%{version}.tar.xz
Requires:   python3-base
Requires:   python3-yaml
Requires:   python3-lxml
Requires:   /usr/bin/xmllint

%description
Script that converts .yaml structures to suitable rpm patterns and package groups.


%package tests
Summary:    Tests for %{name}
Requires:   %{name} = %{version}-%{release}
Requires:   diffutils

%description tests
%{summary}.


%prep
%setup -q -n %{name}-%{version}

%build

%install
rm -rf %{buildroot}
%make_install

%files
%defattr(-,root,root,-)
%license COPYING
%{_bindir}/%{name}.py

%files tests
%defattr(-,root,root,-)
/opt/tests/repomd-pattern-builder/tests.xml
/opt/tests/repomd-pattern-builder/data/*
