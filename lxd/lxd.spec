# If any of the following macros should be set otherwise,
# you can wrap any of them with the following conditions:
# - %%if 0%%{centos} == 7
# - %%if 0%%{?rhel} == 7
# - %%if 0%%{?fedora} == 23
# Or just test for particular distribution:
# - %%if 0%%{centos}
# - %%if 0%%{?rhel}
# - %%if 0%%{?fedora}
#
# Be aware, on centos, both %%rhel and %%centos are set. If you want to test
# rhel specific macros, you can use %%if 0%%{?rhel} && 0%%{?centos} == 0 condition.
# (Don't forget to replace double percentage symbol with single one in order to apply a condition)

# Generate devel rpm
%global with_devel 1
# Build project from bundled dependencies
%global with_bundled 1
# Build with debug info rpm
%global with_debug 1
# Run tests in check section
%global with_check 1
# Generate unit-test rpm
%global with_unit_test 1

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%if 0%{?centos}
# centos doesn't (yet) define build macros for golang
%define gobuild(o:) %{expand:
  go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}'" -a -v -x %{?**};
}
# Define commands for testing
%define gotestflags      -buildmode pie -compiler gc
%define gotestextldflags %__global_ldflags %{?__golang_extldflags}
%define gotest() go test %{gotestflags} -ldflags "${LDFLAGS:-} -extldflags '%{gotestextldflags}'" %{?**};
%endif

%global provider        github
%global provider_tld    com
%global project         lxc
%global repo            lxd
# https://github.com/lxc/lxd
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           lxd
Version:        3.18
Release:        0.1%{?dist}
Summary:        Container hypervisor based on LXC
License:        ASL 2.0
URL:            https://linuxcontainers.org/lxd
Source0:        https://linuxcontainers.org/downloads/%{name}/%{name}-%{version}.tar.gz
Source1:        %{name}.socket
Source2:        %{name}.service
Source3:        lxd-containers.service
Source4:        lxd.dnsmasq
Source5:        lxd.logrotate
Source6:        shutdown
Source7:        lxd.sysctl
Source8:        lxd.profile

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:  aarch64 %{arm} ppc64le s390x x86_64
%endif

# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

BuildRequires:  chrpath
BuildRequires:  gettext
BuildRequires:  help2man
BuildRequires:  libacl-devel
BuildRequires:  libcap-devel
BuildRequires:  libseccomp-devel
BuildRequires:  pkgconfig(lxc)
BuildRequires:  systemd
# tclsh required by embedded sqlite3 build
BuildRequires:  tcl
# required by embedded dqlite build
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  libuv-devel

Requires: acl
Requires: dnsmasq
Requires: ebtables
Requires: iptables
Requires: lxd-client = %{version}-%{release}
Requires: lxcfs
Requires: rsync
Requires: shadow-utils >= 4.1.5
Requires: squashfs-tools
Requires: tar
Requires: xdelta
Requires: xz
%{?systemd_requires}
Requires(pre): container-selinux >= 2:2.38
Requires(pre): shadow-utils
# Do not require bundled libraries
%global __requires_exclude libsqlite3.so.0
%global __requires_exclude %{__requires_exclude}|libco.so
%global __requires_exclude %{__requires_exclude}|libraft.so.0
%global __requires_exclude %{__requires_exclude}|libdqlite.so.0

Provides:       bundled(libsqlite3.so.0()) = e131dd7676fea1a0e101bfe0f25744bc9c4f9a69
Provides:       bundled(libco.so()) = b8b70b0cf5d6c6521174001133bb4fde6cce761a
Provides:       bundled(libraft.so.0()) = 7d7f93b3ec75d1e26c02d1c30de9ff9a774492bc
Provides:       bundled(libdqlite.so.0()) = 5490b4028b3217391a49a73ee37d46b750eb1e3b
# Do not auto-provide .so files in the application-specific library directory
%global __provides_exclude_from %{_libdir}/%{name}/.*\\.so

%description
Container hypervisor based on LXC
LXD offers a REST API to remotely manage containers over the network,
using an image based work-flow and with support for live migration.

This package contains the LXD daemon.

%if 0%{?with_devel}
%package devel
Summary:        Container hypervisor based on LXC - Source Libraries
BuildArch:      noarch

%if 0%{?with_check}
# CentOS 8 doesn't support Btrfs
%if 0%{?fedora} || ( 0%{?centos} && 0%{?centos} < 8 )
BuildRequires:  btrfs-progs
%endif
BuildRequires:  dnsmasq
%endif

Provides:       golang(%{import_path}/client) = %{version}-%{release}
Provides:       golang(%{import_path}/lxc/config) = %{version}-%{release}
Provides:       golang(%{import_path}/lxc/utils) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/apparmor) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/cluster) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/cluster/raft) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/config) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/db) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/db/cluster) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/db/node) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/db/query) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/db/schema) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/device) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/device/config) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/dnsmasq) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/endpoints) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/events) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/instance/instancetype) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/instance/operationlock) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/iptables) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/maas) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/migration) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/node) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/operations) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/project) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/rbac) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/resources) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/response) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/seccomp) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/state) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/storage) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/storage/quota) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/sys) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/task) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/template) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/ucred) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd/util) = %{version}-%{release}
Provides:       golang(%{import_path}/lxd-benchmark/benchmark) = %{version}-%{release}
Provides:       golang(%{import_path}/shared) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/api) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/cancel) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/cmd) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/containerwriter) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/dnsutil) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/eagain) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/generate/db) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/generate/file) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/generate/lex) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/i18n) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/idmap) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/ioprogress) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/log15) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/log15/stack) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/log15/term) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/logger) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/logging) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/netutils) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/osarch) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/simplestreams) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/termios) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/units) = %{version}-%{release}
Provides:       golang(%{import_path}/shared/version) = %{version}-%{release}

%if 0%{?with_bundled}
# Avoid duplicated Provides of bundled libraries
Autoprov:       0
Provides:       lxd-devel = %{version}-%{release}

# generated from dist/MANIFEST
Provides:       bundled(golang(github.com/boltdb/bolt)) = fd01fc79c553a8e99d512a07e8e0c63d4a3ccfc5
Provides:       bundled(golang(github.com/canonical/go-dqlite)) = 6538c9689022a97e358e9ad85f94af974c01397e
Provides:       bundled(golang(github.com/canonical/go-dqlite/client)) = 6538c9689022a97e358e9ad85f94af974c01397e
Provides:       bundled(golang(github.com/canonical/go-dqlite/driver)) = 6538c9689022a97e358e9ad85f94af974c01397e
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient/candidtest)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient/params)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient/redirect)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient/ussodischarge)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/CanonicalLtd/candidclient/ussologin)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(github.com/cpuguy83/go-md2man)) = f79a8a8ca69da163eee19ab442bedad7a35bba5a
Provides:       bundled(golang(github.com/cpuguy83/go-md2man/md2man)) = f79a8a8ca69da163eee19ab442bedad7a35bba5a
Provides:       bundled(golang(github.com/dustinkirkland/golang-petname)) = 11339a705ed2dfd341d0b99e95b478dd0d8366ef
Provides:       bundled(golang(github.com/flosch/pongo2)) = bbf5a6c351f4d4e883daa40046a404d7553e0a00
Provides:       bundled(golang(github.com/golang/protobuf/descriptor)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/jsonpb)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/jsonpb/jsonpb_test_proto)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/proto)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/protoc-gen-go)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/protoc-gen-go/descriptor)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/protoc-gen-go/generator)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/protoc-gen-go/grpc)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/protoc-gen-go/plugin)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/proto/proto3_proto)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/proto/test_proto)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/any)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/duration)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/empty)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/struct)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/timestamp)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/golang/protobuf/ptypes/wrappers)) = 1680a479a2cfb3fa22b972af7e36d0a0fde47bf8
Provides:       bundled(golang(github.com/google/gopacket)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/afpacket)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/bsdbpf)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/bytediff)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/defrag/lcmdefrag)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/dumpcommand)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/ip4defrag)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/layers)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/macs)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/pcap)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/pcapgo)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/pcap/gopacket_benchmark)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/pfring)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/reassembly)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/routing)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/tcpassembly)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/gopacket/tcpassembly/tcpreader)) = 33810c487ced200c983df5c45e3ebd2adc404b71
Provides:       bundled(golang(github.com/google/uuid)) = c2e93f3ae59f2904160ceaab466009f965df46d6
Provides:       bundled(golang(github.com/gorilla/mux)) = 884b5ffcbd3a11b730f0b75f5c86ac408753c34d
Provides:       bundled(golang(github.com/gorilla/websocket)) = c3e18be99d19e6b3e8f1559eea2c161a665c4b6b
Provides:       bundled(golang(github.com/gosexy/gettext)) = 74466a0a0c4a62fea38f44aa161d4bbfbe79dd6b
Provides:       bundled(golang(github.com/gosexy/gettext/go-xgettext)) = 74466a0a0c4a62fea38f44aa161d4bbfbe79dd6b
Provides:       bundled(golang(github.com/hashicorp/go-msgpack/codec)) = ad60660ecf9c5a1eae0ca32182ed72bab5807961
Provides:       bundled(golang(github.com/jaypipes/pcidb)) = 98ef3ee36c69f20650fe7855047ad042338c6983
Provides:       bundled(golang(github.com/juju/collections/deque)) = 9be91dc79b7c185fa8b08e7ceceee40562055c83
Provides:       bundled(golang(github.com/juju/collections/set)) = 9be91dc79b7c185fa8b08e7ceceee40562055c83
Provides:       bundled(golang(github.com/juju/errors)) = d42613fe1ab9e303fc850e7a19fda2e8eeb6516e
Provides:       bundled(golang(github.com/juju/go4/bytereplacer)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/cloud/cloudlaunch)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/cloud/google/gceutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/cloud/google/gcsutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/ctxutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/errorutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/fault)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/jsonconfig)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/legal)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/lock)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/net/throttle)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/oauthutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/osutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/readerutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/strutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/syncutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/syncutil/singleflight)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/syncutil/syncdebug)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/types)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/wkfs)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/wkfs/gcs)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/go4/writerutil)) = 40d72ab9641a2a8c36a9c46a51e28367115c8e59
Provides:       bundled(golang(github.com/juju/gomaasapi)) = 0ab1eb636aba97733a62e850ffea2c8729bf9718
Provides:       bundled(golang(github.com/juju/gomaasapi/templates)) = 0ab1eb636aba97733a62e850ffea2c8729bf9718
Provides:       bundled(golang(github.com/juju/httprequest)) = 77d36ac4b71a6095506c0617d5881846478558cb
Provides:       bundled(golang(github.com/juju/loggo)) = 6e530bcce5d8e1b51b8e5ee7f08a455cd0a8c2e5
Provides:       bundled(golang(github.com/juju/loggo/loggocolor)) = 6e530bcce5d8e1b51b8e5ee7f08a455cd0a8c2e5
Provides:       bundled(golang(github.com/juju/persistent-cookiejar)) = d5e5a8405ef9633c84af42fbcc734ec8dd73c198
Provides:       bundled(golang(github.com/juju/schema)) = 1f8aaeef09898fcee40fe43b8de422533b0cac2b
Provides:       bundled(golang(github.com/juju/utils)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/arch)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/bzr)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/cache)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/cert)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/debugstatus)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/deque)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/du)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/exec)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/featureflag)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/filepath)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/filestorage)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/fs)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/hash)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/jsonhttp)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/keyvalues)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/mgokv)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/os)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/parallel)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/proxy)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/readpass)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/registry)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/series)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/set)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/shell)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/ssh)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/symlink)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/tailer)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/tar)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/uptime)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/voyeur)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/winrm)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/utils/zip)) = bf9cc5bdd62dabc40b7f634b39a5e2dc44d44c45
Provides:       bundled(golang(github.com/juju/version)) = b64dbd566305c836274f0268fa59183a52906b36
Provides:       bundled(golang(github.com/juju/webbrowser)) = efb9432b2bcb671b0cf2237468e209d10e2ac373
Provides:       bundled(golang(github.com/julienschmidt/httprouter)) = 7072f59069b7dfa4273a1febe87a643e75632578
Provides:       bundled(golang(github.com/mattn/go-colorable)) = 98ec13f34aabf44cc914c65a1cfb7b9bc815aef1
Provides:       bundled(golang(github.com/mattn/go-isatty)) = bf9a1dea1961e1d831824fb135332bfb8c10e8b8
Provides:       bundled(golang(github.com/mattn/go-runewidth)) = 703b5e6b11ae25aeb2af9ebb5d5fdf8fa2575211
Provides:       bundled(golang(github.com/mattn/go-sqlite3)) = 4396a38886da660e403409e35ef4a37906bf0975
Provides:       bundled(golang(github.com/mattn/go-sqlite3/upgrade)) = 4396a38886da660e403409e35ef4a37906bf0975
Provides:       bundled(golang(github.com/mdlayher/eui64)) = eee6532bb9adf30c2a17e9963ed90aa14161dae9
Provides:       bundled(golang(github.com/miekg/dns)) = 1208fbdde0ad3326de82ac4a8f53058d480ed228
Provides:       bundled(golang(github.com/miekg/dns/dnsutil)) = 1208fbdde0ad3326de82ac4a8f53058d480ed228
Provides:       bundled(golang(github.com/mitchellh/go-homedir)) = af06845cf3004701891bf4fdb884bfe4920b3727
Provides:       bundled(golang(github.com/mpvl/subtest)) = f6e4cfd4b9ea1beb9fb5d53afba8c30804a02ae7
Provides:       bundled(golang(github.com/olekukonko/tablewriter)) = cc27d85e17cec9768d2ac401ea5d619a9628f16d
Provides:       bundled(golang(github.com/olekukonko/tablewriter/csv2table)) = cc27d85e17cec9768d2ac401ea5d619a9628f16d
Provides:       bundled(golang(github.com/pborman/uuid)) = 8b1b92947f46224e3b97bb1a3a5b0382be00d31e
Provides:       bundled(golang(github.com/pkg/errors)) = 27936f6d90f9c8e1145f11ed52ffffbfdb9e0af7
Provides:       bundled(golang(github.com/Rican7/retry)) = 272ad122d6e5ce1be757544007cf8bcd1c9c9ab0
Provides:       bundled(golang(github.com/Rican7/retry/backoff)) = 272ad122d6e5ce1be757544007cf8bcd1c9c9ab0
Provides:       bundled(golang(github.com/Rican7/retry/jitter)) = 272ad122d6e5ce1be757544007cf8bcd1c9c9ab0
Provides:       bundled(golang(github.com/Rican7/retry/strategy)) = 272ad122d6e5ce1be757544007cf8bcd1c9c9ab0
Provides:       bundled(golang(github.com/rogpeppe/fastuuid)) = 10c3923834d38e951ae8f627bfec2dc632c5b6cb
Provides:       bundled(golang(github.com/spf13/cobra)) = 19cf35ea77e5981f8e8b90a897af621f2be864f6
Provides:       bundled(golang(github.com/spf13/cobra/cobra)) = 19cf35ea77e5981f8e8b90a897af621f2be864f6
Provides:       bundled(golang(github.com/spf13/cobra/cobra/tpl)) = 19cf35ea77e5981f8e8b90a897af621f2be864f6
Provides:       bundled(golang(github.com/spf13/cobra/doc)) = 19cf35ea77e5981f8e8b90a897af621f2be864f6
Provides:       bundled(golang(github.com/spf13/pflag)) = 2e9d26c8c37aae03e3f9d4e90b7116f5accb7cab
Provides:       bundled(golang(github.com/stretchr/testify)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/stretchr/testify/assert)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/stretchr/testify/http)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/stretchr/testify/mock)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/stretchr/testify/require)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/stretchr/testify/suite)) = 85f2b59c4459e5bf57488796be8c3667cb8246d6
Provides:       bundled(golang(github.com/syndtr/gocapability/capability)) = d98352740cb2c55f81556b63d4a1ec64c5a319c2
Provides:       bundled(golang(github.com/syndtr/gocapability/capability/enumgen)) = d98352740cb2c55f81556b63d4a1ec64c5a319c2
Provides:       bundled(golang(golang.org/x/crypto/acme)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/acme/autocert)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/argon2)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/bcrypt)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/blake2b)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/blake2s)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/blowfish)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/bn256)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/cast5)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/chacha20poly1305)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/cryptobyte)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/cryptobyte/asn1)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/curve25519)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ed25519)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/hkdf)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/md4)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/nacl/auth)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/nacl/box)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/nacl/secretbox)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/nacl/sign)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ocsp)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/armor)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/clearsign)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/elgamal)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/errors)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/packet)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/openpgp/s2k)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/otr)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/pbkdf2)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/pkcs12)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/poly1305)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ripemd160)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/salsa20)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/salsa20/salsa)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/scrypt)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/sha3)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ssh)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ssh/agent)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ssh/knownhosts)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/ssh/terminal)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/tea)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/twofish)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/xtea)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/crypto/xts)) = f9e2070545dcd4128a854a97ddf10fbfc3c4b6e4
Provides:       bundled(golang(golang.org/x/net/bpf)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/context)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/context/ctxhttp)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/dict)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/dns/dnsmessage)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/html)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/html/atom)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/html/charset)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http2)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http2/h2c)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http2/h2demo)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http2/h2i)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http2/hpack)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http/httpguts)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/http/httpproxy)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/icmp)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/idna)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/ipv4)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/ipv6)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/lif)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/nettest)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/netutil)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/proxy)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/publicsuffix)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/route)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/trace)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/webdav)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/websocket)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/net/xsrftoken)) = 2ec189313ef0a07735684caebd1ba8b8ebca456f
Provides:       bundled(golang(golang.org/x/sys/cpu)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/plan9)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/unix)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/unix/linux)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows/registry)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows/svc)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows/svc/debug)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows/svc/eventlog)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(golang.org/x/sys/windows/svc/mgr)) = b397fe3ad8ed895c98fa54584f61835a88e65ff5
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1/candidtest)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1/params)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1/redirect)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1/ussodischarge)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/CanonicalLtd/candidclient.v1/ussologin)) = eb84dcf98f4ff1f7f8149ec39f470dc6dda61d63
Provides:       bundled(golang(gopkg.in/errgo.v1)) = 08dc5b27f5ced65786776ec936b4298445ec70cf
Provides:       bundled(golang(gopkg.in/fsnotify.v0)) = ea925a0a47d225b2ca7f9932b01d2ed4f3ec74f6
Provides:       bundled(golang(gopkg.in/httprequest.v1)) = 7f3c32e65ad57476ba9675100248f4f87f6ffb9c
Provides:       bundled(golang(gopkg.in/juju/environschema.v1)) = d79e96fb1039e808c217847f4c45cce48e6ff2a5
Provides:       bundled(golang(gopkg.in/juju/environschema.v1/form)) = d79e96fb1039e808c217847f4c45cce48e6ff2a5
Provides:       bundled(golang(gopkg.in/lxc/go-lxc.v2)) = f4822c6bba64fd060f8e96393540d6525a7ceb95
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery/checkers)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery/dbrootkeystore)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery/identchecker)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery/mgorootkeystore)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakery/postgresrootkeystore)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/bakerytest)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/httpbakery)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/httpbakery/agent)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon-bakery.v2/httpbakery/form)) = a0743b6619d68bbf8dc5cabbb49738b846f06080
Provides:       bundled(golang(gopkg.in/macaroon.v2)) = 1679699b0b723e05f9f16c45b4c6cbd46adb2c78
Provides:       bundled(golang(gopkg.in/mgo.v2)) = a6b53ec6cb22a3699387a57a161566f9402ee85b
Provides:       bundled(golang(gopkg.in/mgo.v2/bson)) = a6b53ec6cb22a3699387a57a161566f9402ee85b
Provides:       bundled(golang(gopkg.in/mgo.v2/txn)) = a6b53ec6cb22a3699387a57a161566f9402ee85b
Provides:       bundled(golang(gopkg.in/retry.v1)) = cd7d3b308163f575bf3e14623edd50ef2b90b877
Provides:       bundled(golang(gopkg.in/robfig/cron.v2)) = be2e0b0deed5a68ffee390b4583a13aff8321535
Provides:       bundled(golang(gopkg.in/tomb.v2)) = d5d1b5820637886def9eef33e03a27a9f166942c
Provides:       bundled(golang(gopkg.in/yaml.v2)) = bb4e33bf68bf89cad44d386192cbed201f35b241
%endif

%description devel
LXD offers a REST API to remotely manage containers over the network,
using an image based work-flow and with support for live migration.

This package contains library sources intended for
building other packages which use the import path
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test-devel
Summary:        Unit tests for %{name} package
BuildArch:      noarch
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

# test subpackage tests code from devel subpackage
Requires:       %{name}-devel = %{version}-%{release}

%if ! 0%{?with_bundled}
Requires:       golang(github.com/mattn/go-sqlite3)
Requires:       golang(github.com/mpvl/subtest)
Requires:       golang(github.com/stretchr/testify/assert) >= 1.2.0
Requires:       golang(github.com/stretchr/testify/require) >= 1.2.0
Requires:       golang(github.com/stretchr/testify/suite) >= 1.2.0
%endif

%description unit-test-devel
%{summary}.

This package contains unit tests for project providing packages
with %{import_path} prefix.
%endif

%package client
Summary:        Container hypervisor based on LXC - Client

Requires:       gettext

%description client
LXD offers a REST API to remotely manage containers over the network,
using an image based work-flow and with support for live migration.

This package contains the command line client.

%package tools
Summary:        Container hypervisor based on LXC - Extra Tools

%description tools
LXD offers a REST API to remotely manage containers over the network,
using an image based work-flow and with support for live migration.

This package contains extra tools provided with LXD.
 - fuidshift - A tool to map/unmap filesystem uids/gids
 - lxc-to-lxd - A tool to migrate LXC containers to LXD
 - lxd-benchmark - A LXD benchmark utility

%package p2c
Summary:        A physical to container migration tool
#Requires:       netcat
Requires:       rsync

%description p2c
Physical to container migration tool

This tool lets you turn any Linux filesystem (including your current one)
into a LXD container on a remote LXD host.

It will setup a clean mount tree made of the root filesystem and any
additional mount you list, then transfer this through LXD's migration
API to create a new container from it.

%package doc
Summary:        Container hypervisor based on LXC - Documentation
BuildArch:      noarch

%description doc
LXD offers a REST API to remotely manage containers over the network,
using an image based work-flow and with support for live migration.

This package contains user documentation.

%prep
%setup -q -n %{name}-%{version}

%build
%if 0%{?with_bundled}
src_dir=$(pwd)/_dist/deps

# build embedded libsqlite3
pushd _dist/deps/sqlite
%configure --enable-replication --disable-amalgamation --disable-tcl --libdir=%{_libdir}/%{name}
make %{?_smp_mflags}
popd

# build embedded libco
pushd _dist/deps/libco
make %{?_smp_mflags}
popd

# build embedded raft
pushd _dist/deps/raft
autoreconf -i
%configure --libdir=%{_libdir}/%{name}
make %{?_smp_mflags}
popd

# build embedded dqlite
pushd _dist/deps/dqlite
autoreconf -i
PKG_CONFIG_PATH="${src_dir}/sqlite/:${src_dir}/libco/:${src_dir}/raft/" %configure --libdir=%{_libdir}/%{name}
make %{?_smp_mflags} CFLAGS="$RPM_OPT_FLAGS -I${src_dir}/sqlite/ -I${src_dir}/libco/ -I${src_dir}/raft/include/" LDFLAGS="-L${src_dir}/sqlite/.libs/ -L${src_dir}/libco/ -L${src_dir}/raft/.libs/"
popd

mkdir _output
pushd _output
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s $(dirs +1 -l) src/%{import_path}
popd

# Move bundled libraries to vendor directory for proper devel packaging
test -d vendor || mkdir vendor
cp -rp _dist/src/. vendor
rm -rf _dist/src

ln -s vendor src
export GOPATH=$(pwd)/_output:$(pwd):%{gopath}
%else
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../ src/%{import_path}

export GOPATH=$(pwd):%{gopath}
%endif

# don't use LDFLAGS='-Wl,-z relro ' from redhat-rpm-config to avoid error:
# "flag provided but not defined: -Wl,-z,relro"
unset LDFLAGS

# LXD depends on a patched, bundled sqlite with replication capabilities
export CGO_CFLAGS="-I${src_dir}/sqlite/ -I${src_dir}/libco/ -I${src_dir}/raft/include/ -I${src_dir}/dqlite/include/"
export CGO_LDFLAGS="-L${src_dir}/sqlite/.libs/ -L${src_dir}/libco/ -L${src_dir}/raft/.libs/ -L${src_dir}/dqlite/.libs/ -Wl,-rpath,%{_libdir}/%{name}"
export LD_LIBRARY_PATH="${src_dir}/sqlite/.libs/:${src_dir}/libco/:${src_dir}/raft/.libs/:${src_dir}/dqlite/.libs/"

BUILDTAGS="libsqlite3" %gobuild -o _bin/lxd %{import_path}/lxd
%gobuild -o _bin/lxc %{import_path}/lxc
%gobuild -o _bin/fuidshift %{import_path}/fuidshift
%gobuild -o _bin/lxd-benchmark %{import_path}/lxd-benchmark
%gobuild -o _bin/lxd-p2c %{import_path}/lxd-p2c
%gobuild -o _bin/lxc-to-lxd %{import_path}/lxc-to-lxd

# build translations
rm -f po/zh_Hans.po    # remove invalid locale
make %{?_smp_mflags} build-mo

# generate man-pages
_bin/lxd manpage .
_bin/lxc manpage .
help2man _bin/fuidshift -n "uid/gid shifter" --no-info --no-discard-stderr > fuidshift.1
help2man _bin/lxd-benchmark -n "The container lightervisor - benchmark" --no-info --no-discard-stderr > lxd-benchmark.1
help2man _bin/lxd-p2c -n "Physical to container migration tool" --no-info --no-discard-stderr > lxd-p2c.1
help2man _bin/lxc-to-lxd -n "Convert LXC containers to LXD" --no-info --no-discard-stderr > lxc-to-lxd.1

%install
# install binaries
install -D -p -m 0755 _bin/lxc %{buildroot}%{_bindir}/lxc
install -D -p -m 0755 _bin/fuidshift %{buildroot}%{_bindir}/fuidshift
install -D -p -m 0755 _bin/lxd-benchmark %{buildroot}%{_bindir}/lxd-benchmark
install -D -p -m 0755 _bin/lxd-p2c %{buildroot}%{_bindir}/lxd-p2c
install -D -p -m 0755 _bin/lxd %{buildroot}%{_bindir}/%{name}
install -D -p -m 0755 _bin/lxc-to-lxd %{buildroot}%{_bindir}/lxc-to-lxd

# extra configs
install -D -p -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/dnsmasq.d/lxd
install -D -p -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/lxd
install -D -p -m 0644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysctl.d/10-lxd-inotify.conf
install -D -p -m 0644 %{SOURCE8} %{buildroot}%{_sysconfdir}/profile.d/lxd.sh

# install bash completion
install -D -p -m 0644 scripts/bash/lxd-client %{buildroot}%{_datadir}/bash-completion/completions/lxd-client

# install systemd units
install -d -m 0755 %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/

# install shutdown wrapper
install -d -m 0755 %{buildroot}%{_libexecdir}/%{name}
install -p -m 0755 %{SOURCE6} %{buildroot}%{_libexecdir}/%{name}

# install custom libsqlite3/dqlite
install -d -m 0755 %{buildroot}%{_libdir}/%{name}
cp -Pp _dist/deps/sqlite/.libs/libsqlite3.so* %{buildroot}%{_libdir}/%{name}/
cp -Pp _dist/deps/libco/libco.so* %{buildroot}%{_libdir}/%{name}/
ln -s libco.so.0.1.0 %{buildroot}%{_libdir}/%{name}/libco.so
ln -s libco.so.0.1.0 %{buildroot}%{_libdir}/%{name}/libco.so.0
cp -Pp _dist/deps/raft/.libs/libraft.so* %{buildroot}%{_libdir}/%{name}/
cp -Pp _dist/deps/dqlite/.libs/libdqlite.so* %{buildroot}%{_libdir}/%{name}/
# fix rpath
chrpath -r %{_libdir}/%{name} %{buildroot}%{_libdir}/%{name}/libdqlite.so

# install man-pages
install -d -m 0755 %{buildroot}%{_mandir}/man1
cp -p lxd.1 %{buildroot}%{_mandir}/man1/
cp -p lxc*.1 %{buildroot}%{_mandir}/man1/
cp -p fuidshift.1 %{buildroot}%{_mandir}/man1/
cp -p lxd-benchmark.1 %{buildroot}%{_mandir}/man1/
cp -p lxd-p2c.1 %{buildroot}%{_mandir}/man1/
cp -p lxc-to-lxd.1 %{buildroot}%{_mandir}/man1/

# cache and log directories
install -d -m 0711 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 0755 %{buildroot}%{_localstatedir}/log/%{name}

# language files
install -d -m 0755 %{buildroot}%{_datadir}/locale
for mofile in po/*.mo ; do
install -D -p -m 0644 ${mofile} %{buildroot}%{_datadir}/locale/$(basename ${mofile%%.mo})/LC_MESSAGES/%{name}.mo
done
%find_lang lxd

# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}%{_includedir}/%{name}
echo "%%dir %%{_includedir}/%%{name}/." >> devel.file-list
cp -pav _dist/deps/sqlite/{sqlite3,sqlite3ext}.h %{buildroot}%{_includedir}/%{name}/
cp -pav _dist/deps/libco/libco.h %{buildroot}%{_includedir}/%{name}/
cp -pav _dist/deps/raft/include/raft.h %{buildroot}%{_includedir}/%{name}/
cp -pav _dist/deps/dqlite/include/dqlite.h %{buildroot}%{_includedir}/%{name}/
echo "%%{_includedir}/%%{name}/*.h" >> devel.file-list

install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
# find all *.s, *.c and *.h cgo development files and generate devel.file-list
for file in $(find . -iname "*.s" -o -iname "*.c" -o -iname "*.h"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go" -o -type f -wholename "./test/deps/s*" -o -type f -wholename ".*/testdata/*"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}

# Add libsqlite3 tag to go test
%define gotestflags -buildmode pie -compiler gc -v -tags libsqlite3

# Tests must ignore potential LXD_SOCKET from environment
unset LXD_SOCKET

# Enable sqlite/dqlite multi-thread support when running unit tests
export GO_DQLITE_MULTITHREAD=1

# Test against the libraries which just built
export CGO_CPPFLAGS="-I%{buildroot}%{_includedir}/%{name}/"
export CGO_LDFLAGS="-L%{buildroot}%{_libdir}/%{name}/"
export LD_LIBRARY_PATH="%{buildroot}%{_libdir}/%{name}/"

%gotest %{import_path}/lxc
# lxc-to-lxd test fails, see ganto/copr-lxc3#10
#%%gotest %%{import_path}/lxc-to-lxd
%gotest %{import_path}/lxd
%gotest %{import_path}/lxd/cluster
%gotest %{import_path}/lxd/config
%gotest %{import_path}/lxd/db
%gotest %{import_path}/lxd/db/cluster
%gotest %{import_path}/lxd/db/node
%gotest %{import_path}/lxd/db/query
%gotest %{import_path}/lxd/db/schema
%gotest %{import_path}/lxd/device/config
%gotest %{import_path}/lxd/endpoints
%gotest %{import_path}/lxd/node
%gotest %{import_path}/lxd/task
%gotest %{import_path}/lxd/util
%gotest %{import_path}/shared
%gotest %{import_path}/shared/idmap
# test fails, see ganto/copr-lxc3#13
#%%gotest %%{import_path}/shared/generate/db
#%%gotest %%{import_path}/shared/generate/lex
%gotest %{import_path}/shared/osarch
%gotest %{import_path}/shared/version
%endif

%pre
# check for existence of lxd group, create it if not found
getent group %{name} > /dev/null || groupadd -f -r %{name}
exit 0

%post
%systemd_post %{name}.socket
%systemd_post %{name}.service
%systemd_post %{name}-container.service

%preun
%systemd_preun %{name}.socket
%systemd_preun %{name}.service
%systemd_preun %{name}-container.service

%postun
%systemd_postun %{name}.socket
%systemd_postun %{name}.service
%systemd_postun %{name}-container.service

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license COPYING
%doc AUTHORS
%config(noreplace) %{_sysconfdir}/dnsmasq.d/lxd
%config(noreplace) %{_sysconfdir}/logrotate.d/lxd
%config(noreplace) %{_sysconfdir}/sysctl.d/10-lxd-inotify.conf
%config(noreplace) %{_sysconfdir}/profile.d/lxd.sh
%{_bindir}/%{name}
%{_unitdir}/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/*
%{_mandir}/man1/%{name}.1.gz
%dir %{_localstatedir}/log/%{name}
%defattr(-, root, root, 0711)
%dir %{_localstatedir}/lib/%{name}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license COPYING
%doc AUTHORS
%endif

%if 0%{?with_unit_test}
%files unit-test-devel -f unit-test.file-list
%license COPYING
%endif

%files client -f lxd.lang
%license COPYING
%{_bindir}/lxc
%{_datadir}/bash-completion/completions/lxd-client
%{_mandir}/man1/lxc.*1.gz

%files tools
%license COPYING
%{_bindir}/fuidshift
%{_bindir}/lxd-benchmark
%{_bindir}/lxc-to-lxd
%{_mandir}/man1/fuidshift.1.gz
%{_mandir}/man1/lxd-benchmark.1.gz
%{_mandir}/man1/lxc-to-lxd.1.gz

%files p2c
%license COPYING
%{_bindir}/lxd-p2c
%{_mandir}/man1/lxd-p2c.1.gz

%files doc
%license COPYING
%doc doc/*

%changelog
* Mon Oct 21 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.17-0.2
- Rebuild for EPEL-8

* Wed Oct 16 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.17-0.1
- Update to 3.17

* Wed Aug 14 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.16-0.1
- Update to 3.16

* Fri Jul 26 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.15-0.1
- Update to 3.15

* Mon Jul 01 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.14-0.1
- Update to 3.14

* Wed May 15 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.13-0.1
- Update to 3.13

* Sat Apr 20 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.12-0.1
- Update to 3.12

* Sat Mar 09 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.11-0.1
- Update to 3.11

* Sun Feb 17 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.10-0.1
- Update to 3.10

* Sun Feb 03 2019 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.9-0.1
- Update to 3.9

* Thu Dec 27 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.8-0.1
- Update to 3.8
- Fix build macros for CentOS and simplify build env variables
- Set --libdir and rpath to avoid LD_LIBRARY_PATH wrapper
- Add upstream patch to fix test failure in github.com/lxc/lxd/lxd
- Generate and package gettext translations

* Sun Sep 30 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.5-0.1
- Update to 3.5
- Fix rpath of embedded libdqlite.so
- Finally fix Provides/Requires of embedded libraries

* Mon Sep 17 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.4-0.1
- Update to 3.4
- Run test with 'libsqlite3' tag
- Install headers of embedded libraries
- Don't auto-provide embedded libraries (e.g. sqlite)

* Fri Aug 10 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.3-0.1
- Update to 3.3

* Wed Jun 27 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.2-0.1
- Update to 3.2

* Thu May 31 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.1-0.3
- Fix build regression with EPEL 7

* Thu May 31 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.1-0.2
- Fix build error on Fedora 26

* Thu May 31 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.1-0.1
- Update to 3.1
- Added LXD_SOCKET override to lxd-containers service (mrd@redhat.com)
- Added support for LXD_SOCKET to lxc-to-lxd

* Thu May 10 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.0.0-0.5
- Fix build with golang-1.8.x (e.g. CentOS <=7.4)
- Experimental patch to fix container startup via LXD_SOCKET

* Fri Apr 27 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.0.0-0.4
- Make sure LXD_SOCKET is not set when running %%check

* Tue Apr 24 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.0.0-0.3
- Add upstream patches according to lxd-3.0.0-0ubuntu4
- Add new sub-package lxd-p2c
- Fix lxd.socket path in systemd .service and .socket

* Sun Apr 15 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.0.0-0.2
- Add bundled modules to devel
- Use new LXD_SOCKET option and set it to /run/lxd.socket
- Add upstream patches according to lxd-3.0.0-0ubuntu3

* Mon Apr 02 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 3.0.0-0.1
- Update to 3.0.0
- Build with bundled go dependencies by default

* Wed Jan 31 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.21-2
- Fix build with bundled go modules
- Correctly specify scriptlet dependencies
- Run systemd preun scriptlet
- Use /usr/libexec instead of /usr/lib for helper script (GH #11)

* Thu Jan 25 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.21-1
- Update to 2.21 (with patches from 2.21-0ubuntu2)

* Tue Jan 23 2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.20-1
- Update to 2.20 (with patches from 2.20-0ubuntu4)
- Major rework of the spec file
- Enable tests

* Fri Nov 03 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.19-2
- Work-around syntax issue on Fedora 27.
- Runtime detect liblxc version.

* Mon Oct 30 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.19-1
- Update to 2.19.
- Update embedded go-lxc to commit 74fb852
- Drop hard dependency to lxc-2.1
- Various RPM metadata fixes

* Wed Oct 04 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.18-3
- Link against libsqlite3
- Update go-sqlite3 dependency to fix startup issue on Fedora 26
- Add upstream patches according to lxd-2.18-0ubuntu3

* Thu Sep 28 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.18-2
- Add upstream patches according to lxd-2.18-0ubuntu2
- Fix xdelta dependency, tighten liblxc version dependency

* Thu Sep 21 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 2.18-1
- Version bump to lxd-2.18
- Update embedded go-lxc to commit 89b06ca

* Mon Aug 28 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.17-3
- Add upstream patches according to lxd-2.17-0ubuntu2

* Thu Aug 24 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.17-2
- Fix man pages wrongly added to multiple packages

* Thu Aug 24 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.17-1
- Version bump to lxd-2.17

* Wed Jul 26 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.16-1
- Version bump to lxd-2.16

* Wed Jul 19 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.15-3
- Tweak timeouts for systemd units
- Add upstream patches according to lxd-2.15-0ubuntu6

* Mon Jul 03 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.15-2
- Rebuild with latest golang-github-gorilla-websocket

* Mon Jul 03 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.15-1
- Version bump to lxd-2.15
- Add upstream patches according to lxd-2.15-0ubuntu4

* Sat Jun 10 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.14-2
- Add some upstream patches according to lxd-2.14-0ubuntu3

* Wed Jun 07 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.14-1
- Version bump to lxd-2.14
- Update embedded go-lxc to commit de2c8bf
- "infinity" for NOFILE doesn't work, set fixed value

* Mon May 01 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.13-1
- Version bump to lxd-2.13
- Add lxc-benchmark to lxd-tools package

* Fri Mar 24 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.12-1
- Version bump to lxd-2.12
- Update embedded go-lxc to commit 8304875

* Thu Mar 09 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.11-1
- Version bump to lxd-2.11
- Add 'lvm-use-ff-with-vgremove.patch' from lxd-2.11-0ubuntu2

* Tue Mar 07 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.10.1-1
- Version bump to lxd-2.10.1

* Thu Mar 02 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.10-1
- Version bump to lxd-2.10, bump websocket dependency due to build errors

* Fri Feb 24 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.9.3-1
- Version bump to lxd-2.9.3

* Tue Feb 21 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.9.2-1
- Version bump to lxd-2.9.2

* Mon Feb 20 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.9.1-1
- Version bump to lxd-2.9.1
- Update embedded go-lxc to commit aeb7ce4

* Thu Jan 26 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.8-1
- Version bump to lxd-2.8, fix some gopath requires/provides

* Tue Dec 27 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.7-1
- Version bump to lxd-2.7, set LXD_DIR to mode 0711
- Add lxc-to-lxd migration script to lxd-tools package

* Wed Dec 14 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.6.2-5
- Don't restrict world access to /var/{lib,log}/lxd

* Sun Dec 11 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.6.2-4
- Fix cache directory permissions, add more suggested packages

* Sat Dec 10 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.6.2-3
- Fix /var/lib/lxd, add shutdown script, new lxd-doc RPM

* Sat Dec 10 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.6.2-2
- Big spec file cleanup, fix devel RPM

* Sun Dec 4 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> - 2.6.2-1
- Initial packaging
