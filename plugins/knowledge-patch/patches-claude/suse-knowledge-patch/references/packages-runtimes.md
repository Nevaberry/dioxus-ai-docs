# Packages, Repositories, and Runtimes

## Leap package transitions

### Python Podman API (`leap-15.6`)

`python-podman` is now built from the `podman-py` project rather than the older
project of the same package name. Validate consumers against the current
`podman-py` API during upgrade.

### Find deprecated packages (`leap-15.6`)

```sh
zypper install lifecycle-data-openSUSE
zypper lifecycle
```

This reports installed packages that are unmaintained and scheduled for removal.

### Leap 15.6 removals (`leap-15.6`)

NVIDIA SUSE Prime supersedes `bbswitch`, `bumblebee`, `bumblebee-status`, and
`primus`. The distribution also removes many unmaintained Python RPMs, including
`python-Keras-Applications`, `python-Theano`, `python-pep517`, `python-pygeos`,
`python-jupytext`, `python-moviepy`, `python-requests-html`, `python-torch`, and
multiple legacy pytest, Jupyter, Dephell, and Spyder plug-ins. Audit RPM-level
dependencies before upgrade.

### Python interpreter strategy (`leap-16.0-guide`)

`/usr/bin/python3` points to Python 3.13 in Leap 16.0 but may move during a
future minor update. Distribution tools are being decoupled so a prior
interpreter can coexist temporarily as a legacy version. Applications must not
assume that `/usr/bin/python3` is permanently fixed to one minor version.

### IA32 applications, Steam, and Wine (`leap-16.0-guide`)

Leap 16 supports only 64-bit binaries. Static 32-bit binaries and all 32-bit
container images cannot run; x86-64 can enable 32-bit syscalls using
`ia32_emulation`. Steam moves from Non-OSS to Flatpak and needs
`grub2-compat-ia32` plus a reboot; SELinux systems may also need
`selinux-policy-targeted-gaming`. Packaged Wine 10.10 is WoW64-only.

### Removed Leap 16 compatibility packages (`leap-16.0-guide`)

Leap 16 removes SysV `init.d`, WSL1, `nscd`, `rc<service>` controls, `criu`, and
`compat-libpthread-nonshared`; replace `crun` with `runc`. `/etc/services` is a
dummy file, so software must not assume it exists before appending entries.

HexChat is no longer packaged; use Polari or Flatpak. Leap 16 carries the last
`nmap` under its former compatible license and plans a different replacement in
a later release.

`mcphost` (configured with no permissions by default) and `lklfuse` are
unsupported technology previews. `lklfuse` lacks Btrfs support because it
handles one device per mount and cannot handle Btrfs multi-device filesystems.

### Parallel package downloads (`leap-16.0`)

Zypper supports parallel downloads for faster installs and updates.

## SLES 15 SP6 modules and support

### Container registries and RPM NDB

Docker Hub and the openSUSE Registry are no longer preconfigured; add them to
`/etc/containers/registries.conf` when needed. Registering the base product
disables a WSL image's free `SLE_BCI` repository.

The `suse/sle15` image uses RPM's NDB backend. Host-side scanners, diff tools,
and builders must use an RPM implementation capable of NDB, such as SLE 15 SP2
or later.

### PostgreSQL and pgAdmin

PostgreSQL receives ordinary product support without an external contract.
PostgreSQL 16 is added; PostgreSQL 15 is deprecated and moves to the Legacy
Module. `pgadmin4` 8.5 moves to the Python 3 Module.

### Development and automation boundaries

`clang` and `llvm17` are dependency-only and unsupported. `ansible-core` is
included, but support covers only playbooks and roles supplied by SLES or its
management products, including dynamically generated integrated content.

### Python, glibc, and Java placement

`python311-base` and `libpython3_11-1_0` move to Basesystem but retain the
Python 3 Module lifecycle. glibc 2.38 splits deprecated `libnsl1` into its own
package. Java 8, 11, and 17 move to Legacy; Java 21 is in Base System. IBM Java
was externally supported only through 2025-04-30 and was scheduled for removal
in SP7.

### Other package and module changes

- `libapr1-devel` becomes `apr-devel`.
- `libapr-util1-devel` becomes `apr-util-devel`.
- The Systems Management Module carries packages such as Ansible.
- `xorriso` becomes CLI-only; its GUI moves to `xorriso-tcltk`.
- `sysctl-logger` adds BPF-based sysctl-change monitoring.
- `rpm-imaevmsign` supplies the IMA/EVM RPM signing plug-in.

### Technology previews

The AMD Navi32 “Wheat Nas” driver remains a preview because matching firmware
is unavailable. Intel IAA crypto-compression is also a preview. The disabled-by-
default Confidential Computing Module is a preview whose host, secure-VM, and
remote-attestation tooling is unsupported.

### Search across SLE modules

`zypper search-packages` searches enabled and disabled modules through SCC and
also works through RMT:

```sh
zypper search-packages SEARCH_TERM
```

### Removed packages, drivers, and cloud dependencies

`docker-runc` is replaced by `runc`; `timezone-java`, insecure `dpt_i2o`, and
`openmpi2`/`openmpi3` are removed. The Public Cloud Module drops componentized
Azure CLI packages, legacy Google cloud agents and SDK, packaged Terraform
providers, `WALinuxAgent`, and related deployment helpers. Audit cloud-image
and automation RPM dependencies.

PHP 7.4 and `numad` were scheduled for SP7 removal. Replace `sev-tool` with
`sevctl` and `gnote` with `bijiben`. OpenLDAP support ends with the SP6 lifecycle
in favor of 389 Directory Server. SP7 removes `ceph-common`, `libcephfs-devel`,
`python3-ceph-common`, `python3-rbd`, and `python3-rgw`; `intel-opencl` and
`intel-graphics-compiler` move to Package Hub.

## SLES 15 SP7 package turnover

### Languages and databases

SP7 adds Ruby 3.4 beside Ruby 2.5, changes the `postgresql` meta-package from 16
to 17, adds PostgreSQL 17.4, adds `pgvector` 0.8 for PostgreSQL 16 and 17, and
adds `postgresql16-pgaudit`.

It adds Python 3.13 tooling, Node.js 22, Go 1.23/1.24, GCC 14, and Rust
1.78/1.85/1.86. The GA comparison removes Python 3.12, Node.js 20, Go
1.20–1.22, GCC 11 and GCC 13 32-bit packages, LLVM 17, and several older
Cargo/Rust lines. Audit versioned RPM dependencies.

### Conflicting database records

The GA comparison records BIND 9.20.3 and MariaDB 11.4.5, while release prose
describes BIND 9.18 and MariaDB 11.8 LTS. Query enabled repositories or installed
RPMs before applying version-specific migration steps.

### Major user-space transitions

GA transitions include OpenSSL 3.1.4→3.2.3, Docker 24.0.7→27.5.1, ClamAV
0.103→1.4, FreeRDP 2.11→3.10, FRR 8.4→10.2, `libfabric` 1.20→2.0, PHP
8.2→8.3, and Wireshark 3.6→4.2. Compatibility packages such as
`docker-stable` 24.0.9 and `freerdp2` are newly present; select them explicitly
rather than assuming the unversioned name remains on the older major.

### HPC turnover

`slurm` moves from 23.02 to 24.11, with `slurm_23_02` still available. Open MPI
4.1.6 package names give way to 4.1.7. The comparison removes HDF5 1.10.11 and
unversioned GNU/MPI HPC families without identifying replacement HDF5 packages;
audit image and module specifications explicitly.

### Redis, time, and keyboard settings

`redis` and `redis7` are removed; use Valkey 8.0.2. `ntp` moves to Legacy before
SLES 16 removes it in favor of Chrony. `KBD_DISABLE_CAPS_LOCK` is removed from
`/etc/sysconfig/keyboard`.

## SLES 16 package model and compatibility

### Management stacks

SUSE Multi-Linux Manager can manage SLES 16 and still uses Salt internally, but
SLES 16 does not ship Salt packages. WBEM through SBLIM packages is removed with
no direct replacement. SLE 15 modules and pool/update channels are also gone;
each SLES 16 minor still requires its own repository transition.

### Supported Java lines

All with L3 support, `java-17-openjdk` is supported through 2027-10-31,
`java-21-openjdk` through 2031-10-31, and `java-25-openjdk` through 2033-10-31.

### Temporary `libnsl.so.1` stub

The real library is removed. `libnsl-stub1` temporarily provides an ABI-
compatible but nonfunctional stub for installers that merely check for the
file. Port applications that call it; the stub itself is scheduled for removal.

### Removed SLES 16 packages

SLES 16 removes `hplip`, `ansible-9`, and `ansible-core-2.16`. Prometheus is
removed because its inclusion was accidental and unsupported.

### Node.js default (`16.0-rev-2026-08-04`)

Node.js 24 is the default; package selection and compatibility checks must not
assume an earlier major line.
