#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)

Summary:	A fast random number generator as a kernel module for Linux.
Summary(pl):	Szybki genereator liczb pseudolosowych w postaci modu�u kernela.
Name:		kernel-char-frandom
Version:	0.8
%define		_rel	1
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/frandom/frandom-%{version}.tar.gz
# Source0-md5:	b46c48721ff545b80a28d8e03e0e3115
Patch0:		%{name}-kdev_t.patch
URL:		http://frandom.freedesktop.org/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
frandom is a kernel module. It's the machinery between a special device driver,
/dev/frandom, which behaves very much like /dev/urandom, only it creates data
faster. Much faster. And it doesn't use much or any kernel entropy.

%package -n kernel-smp-char-frandom
Summary:	A fast random number generator as a SMP kernel module for Linux.
Summary(pl):	Szybki genereator liczb pseudolosowych w postaci modu�u kernela SMP.
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-char-frandom
/dev/frandom, which behaves very much like /dev/urandom, only it creates data
faster. Much faster. And it doesn't use much or any kernel entropy.

%prep
%setup -q -n frandom-%{version}
%patch0 -p1
ln -sf Makefile-2.6 Makefile

%build
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -f *.o
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv frandom.ko frandom-$cfg.ko
done

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/char
cp frandom-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/char/frandom.ko
%if %{with smp} && %{with dist_kernel}
cp frandom-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/char/frandom.ko
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-char-frandom
%depmod %{_kernel_ver}

%postun	-n kernel-char-frandom
%depmod %{_kernel_ver}

%post	-n kernel-smp-char-frandom
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-char-frandom
%depmod %{_kernel_ver}smp

%files -n kernel-char-frandom
%defattr(644,root,root,755)
%doc README CHANGELOG
/lib/modules/%{_kernel_ver}/char/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-char-frandom
%doc README CHANGELOG
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/char/*.ko*
%endif