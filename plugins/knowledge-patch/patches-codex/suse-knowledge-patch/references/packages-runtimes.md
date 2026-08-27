# Packages, Repositories, and Runtimes

## Leap package and runtime changes

The Leap 15.6 `python-podman` package uses the `podman-py` project rather than
the older `python-podman` project. Validate clients against the current API.
(leap-15.6)

Leap 15.6 removes `bbswitch`, `bumblebee`, `bumblebee-status`, and `primus` in
favor of NVIDIA SUSE Prime. It also removes many unmaintained Python RPMs,
including `python-Keras-Applications`, `python-Theano`, `python-pep517`,
`python-pygeos`, `python-jupytext`, `python-moviepy`, `python-requests-html`,
`python-torch`, and legacy pytest, Jupyter, Dephell, and Spyder plug-ins. Audit
RPM-level dependencies before upgrade.

Leap 16 points `/usr/bin/python3` at Python 3.13, but a future minor update may
move it again. Distribution tooling is being decoupled so an earlier interpreter
can coexist temporarily; applications must not assume that path is permanently
pinned. (leap-16.0-guide)

Leap 16 is 64-bit only. Statically linked 32-bit binaries and 32-bit containers
cannot run; x86-64 can enable 32-bit syscalls with `ia32_emulation`. Steam moves
from Non-OSS to Flatpak and requires `grub2-compat-ia32` plus a reboot; SELinux
systems may also need `selinux-policy-targeted-gaming`. Packaged Wine 10.10 is
WoW64-only.

Leap 16 removes SysV `init.d`, WSL1, `nscd`, `rc<service>`, `criu`, and
`compat-libpthread-nonshared`; replace `crun` with `runc`. `/etc/services` is a
dummy, so software must not assume a real file exists before appending entries.
HexChat is removed because upstream is archived; use Polari or Flatpak. The
shipped `nmap` is the final version under its former compatible license and is
planned to be replaced in a later release.

SUSE Linux Enterprise Desktop is not planned for SLES 16.0, which supplies a
minimal GNOME environment. VNC server, GTK2, Qt5, and wxWidgets are removed; use
RDP and port applications to GTK4, Qt6, or another supported toolkit.

## SLES 15 SP6 repositories and modules

Docker Hub and the openSUSE Registry are no longer preconfigured; add required
registries to `/etc/containers/registries.conf`. Registering a WSL image's base
product disables its free `SLE_BCI` repository. The `suse/sle15` container uses
RPM NDB, so host scanners, diff tools, and image builders need an NDB-capable RPM
implementation such as SLE 15 SP2 or later.

PostgreSQL now receives normal product support without an external contract.
PostgreSQL 16 is added, PostgreSQL 15 is deprecated and moves to the Legacy
Module, and `pgadmin4` 8.5 moves to the Python 3 Module.

`clang` and `llvm17` are dependency-only and unsupported. `ansible-core` is
included, but support applies only to playbooks and roles supplied by SLES or
its management products, including dynamically generated integrated content.

`python311-base` and `libpython3_11-1_0` move to Basesystem but retain the Python
3 Module lifecycle. glibc 2.38 splits deprecated `libnsl1` into a separate
package. Java 8, 11, and 17 move to Legacy; Java 21 is in Base System. IBM Java
was externally supported only through 2025-04-30 and scheduled for SP7 removal.

Other SP6 packaging changes include:

- `libapr1-devel` becomes `apr-devel`; `libapr-util1-devel` becomes
  `apr-util-devel`.
- The Systems Management Module carries Ansible and related packages.
- `xorriso` is CLI-only; its GUI is in `xorriso-tcltk`.
- `sysctl-logger` monitors sysctl changes with BPF.
- `rpm-imaevmsign` supplies the IMA/EVM RPM signing plug-in.
- OpenSSL 3.1.4 replaces 1.1.1; remove mutually exclusive
  `libopenssl1_1-devel` manually because conflict resolution is not automatic.
- `libstoragemgmt` 1.9.8 folds in the NetApp plug-in and removes NetApp ONTAP
  and NexentaStor `nstor` plug-ins; replace those integrations before upgrade.

Removed packages include `docker-runc` (use `runc`), `timezone-java`, insecure
`dpt_i2o`, and `openmpi2`/`openmpi3`. The Public Cloud Module also drops
componentized Azure CLI RPMs, legacy Google agents and SDK, packaged Terraform
providers, `WALinuxAgent`, and related helpers; audit cloud-image automation.

PHP 7.4 and `numad` were scheduled for SP7 removal. Replace `sev-tool` with
`sevctl` and `gnote` with `bijiben`. SP7 removes Ceph client packages
`ceph-common`, `libcephfs-devel`, `python3-ceph-common`, `python3-rbd`, and
`python3-rgw`; `intel-opencl` and `intel-graphics-compiler` move to Package Hub.

## SLES 15 SP7 turnover

SP7 adds Ruby 3.4 alongside 2.5; PostgreSQL's meta-package moves from 16 to 17
and adds PostgreSQL 17.4, `pgvector` 0.8 for PostgreSQL 16/17, and
`postgresql16-pgaudit`. It adds Python 3.13 tooling, Node.js 22, Go 1.23/1.24,
GCC 14, and Rust 1.78/1.85/1.86. GA comparison removes Python 3.12, Node.js 20,
Go 1.20-1.22, GCC 11, GCC 13 32-bit packages, LLVM 17, and older Cargo/Rust
lines. Audit versioned RPM dependencies.

Package records conflict for database versions: the GA comparison reports
MariaDB 11.4.5 and `bind` 9.20.3, while release prose reports MariaDB 11.8 LTS
and BIND 9.18. Query enabled repositories or installed RPMs before applying
version-specific advice.

Major transitions include OpenSSL 3.1.4 to 3.2.3, Docker 24.0.7 to 27.5.1,
ClamAV 0.103 to 1.4, FreeRDP 2.11 to 3.10, FRR 8.4 to 10.2, `libfabric` 1.20 to
2.0, PHP 8.2 to 8.3, and Wireshark 3.6 to 4.2. Compatibility names such as
`docker-stable` 24.0.9 and `freerdp2` retain older lines only when explicitly
selected.

The `slurm` meta-package moves from 23.02 to 24.11 while `slurm_23_02` remains.
Open MPI 4.1.6 names move to 4.1.7. GA comparison removes HDF5 1.10.11 and
unversioned GNU/MPI HPC families without naming replacement HDF5 packages, so
audit HPC module and image specifications.

SP7 removes `redis` and `redis7`; use Valkey 8.0.2. `ntp` moves to Legacy ahead
of SLES 16 removal in favor of Chrony. `KBD_DISABLE_CAPS_LOCK` is removed from
`/etc/sysconfig/keyboard`.

## SLES 16 runtimes and compatibility packages

Supported L3 OpenJDK packages are `java-17-openjdk` through 2027-10-31,
`java-21-openjdk` through 2031-10-31, and `java-25-openjdk` through 2033-10-31.

The real `libnsl.so.1` is removed. `libnsl-stub1` temporarily supplies a
nonfunctional ABI-compatible stub for installers that only probe for the file;
port applications that call it because the stub is also scheduled for removal.

SLES 16 removes `hplip`, `ansible-9`, and `ansible-core-2.16`. Prometheus is
also removed because its inclusion was accidental and unsupported.

Node.js 24 becomes the default in the later SLES 16.0 revision; do not assume
the distribution default remains on an earlier major. (16.0-rev-2026-08-04)
