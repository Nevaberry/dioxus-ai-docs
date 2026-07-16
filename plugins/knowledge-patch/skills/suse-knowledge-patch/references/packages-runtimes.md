# Packages, Repositories, and Runtimes

Use this reference to audit RPM dependencies, module placement, language and database transitions, removed packages, and compatibility shims.

## Contents

- [Package discovery and repository behavior](#package-discovery-and-repository-behavior)
- [Python and development tools](#python-and-development-tools)
- [Language and database lines](#language-and-database-lines)
- [HPC package turnover](#hpc-package-turnover)
- [Runtime replacements and compatibility](#runtime-replacements-and-compatibility)
- [Removed and deprecated packages](#removed-and-deprecated-packages)
- [Technology preview and support boundaries](#technology-preview-and-support-boundaries)

## Package discovery and repository behavior

### Deprecated Leap packages

Install lifecycle data and query installed packages that are no longer maintained or are scheduled for removal:

```sh
zypper install lifecycle-data-openSUSE
zypper lifecycle
```

### Cross-module SLE search

Search both enabled and disabled SLE modules through SCC with `zypper search-packages`; SLES 15 SP6 also supports this for RMT-registered systems:

```sh
zypper search-packages SEARCH_TERM
```

### Zypper downloads

Leap 16 supports parallel package downloads for faster installation and updates.

## Python and development tools

### Podman client API

Leap 15.6 bases `python-podman` on the `podman-py` project instead of the former project with the same package role. Test consumers against the current `podman-py` API rather than assuming the old binding's behavior.

### Leap Python strategy

Leap 16 points `/usr/bin/python3` to Python 3.13, but a future minor update may move the path to a newer interpreter. Distribution tools are being decoupled so the former interpreter can temporarily coexist as a legacy version. Do not bind application compatibility to one permanent `/usr/bin/python3` minor version.

### SLES 15 SP6 development support

Treat `clang` and `llvm17` as unsupported dependency-only packages. `ansible-core` is included, but SUSE support covers only playbooks and roles supplied by SLES or its management products, including dynamically generated integrated content.

`python311-base` and `libpython3_11-1_0` move to the Basesystem Module but keep the Python 3 Module lifecycle. The Systems Management Module carries packages such as Ansible.

Rename build dependencies from `libapr1-devel` to `apr-devel` and from `libapr-util1-devel` to `apr-util-devel`. Use `xorriso-tcltk` for the split-out GUI; `xorriso` itself is CLI-only. Use `rpm-imaevmsign` for the IMA/EVM RPM signing plug-in. `sysctl-logger` adds BPF-based sysctl-change monitoring.

## Language and database lines

### PostgreSQL, pgAdmin, and module placement

PostgreSQL now has normal product support without an external contract. PostgreSQL 16 is added, PostgreSQL 15 is deprecated and placed in the Legacy Module, and `pgadmin4` 8.5 moves to the Python 3 Module.

Java 8, 11, and 17 are in the Legacy Module; Java 21 is in Base System. IBM Java was externally supported only through 2025-04-30 and was scheduled for SP7 removal. glibc 2.38 splits deprecated `libnsl1` into its own package.

### Language and database turnover

SP7 adds Ruby 3.4 alongside Ruby 2.5, moves the `postgresql` meta-package from 16 to 17, adds PostgreSQL 17.4, adds `pgvector` 0.8 for PostgreSQL 16 and 17, and adds `postgresql16-pgaudit`.

It adds Python 3.13 tooling, Node.js 22, Go 1.23 and 1.24, GCC 14, and Rust 1.78, 1.85, and 1.86. The GA comparison removes Python 3.12, Node.js 20, Go 1.20–1.22, GCC 11, GCC 13 32-bit packages, LLVM 17, and several older Cargo/Rust lines. Audit versioned RPM dependencies before upgrading.

The SP7 release documentation records conflicting versions for two packages: the GA package comparison lists `bind` 9.20.3 and MariaDB 11.4.5, while the release-note prose describes BIND 9.18 and MariaDB 11.8 LTS. The documentation does not resolve the disagreement, so query the enabled repository or installed RPM before applying version-specific guidance.

Other notable GA transitions include OpenSSL 3.1.4 to 3.2.3, Docker 24.0.7 to 27.5.1, ClamAV 0.103 to 1.4, FreeRDP 2.11 to 3.10, FRR 8.4 to 10.2, `libfabric` 1.20 to 2.0, PHP 8.2 to 8.3, and Wireshark 3.6 to 4.2. Select compatibility packages such as `docker-stable` 24.0.9 and `freerdp2` explicitly rather than assuming unversioned names retain old major lines.

### Supported OpenJDK lines

Use `java-17-openjdk` with L3 support through 2027-10-31, `java-21-openjdk` through 2031-10-31, or `java-25-openjdk` through 2033-10-31.

## HPC package turnover

SLES 15 SP7 moves the `slurm` meta-package from 23.02 to 24.11 while retaining `slurm_23_02`. Open MPI package names move from 4.1.6 to 4.1.7. The GA comparison removes HDF5 1.10.11 and unversioned GNU/MPI HPC families without listing replacement HDF5 packages; audit HPC images and module specifications explicitly.

## Runtime replacements and compatibility

### Redis and time service

SLES 15 SP7 removes `redis` and `redis7` and replaces them with Valkey 8.0.2. The `ntp` package moves to the Legacy Module ahead of SLES 16 removal in favor of Chrony. Remove automation for the deleted `KBD_DISABLE_CAPS_LOCK` setting in `/etc/sysconfig/keyboard`.

### OpenSSL development packages

SLES 15 SP6 OpenSSL 3.1.4 replaces 1.1.1. Because the two development-package lines conflict and update resolution is not automatic, remove `libopenssl1_1-devel` manually during upgrade.

### `libnsl` compatibility

SLES 16 removes the real `libnsl.so.1`. `libnsl-stub1` temporarily provides an ABI-compatible but nonfunctional stub for installers that only probe for the library. Port callers that use its functions; the stub is scheduled for later removal.

### OpenLDAP soname shims

SLES 16 supplies `libldap` and `liblber` shims with OpenLDAP 2.4 sonames linked to OpenLDAP 2.6 for applications such as SAP central user management. They implement only the public API and cannot supply the two GSSAPI functions removed from OpenLDAP 2.6.

### 32-bit applications, Steam, and Wine

Leap 16 supports only 64-bit binaries; statically linked 32-bit applications and 32-bit container images cannot run. On x86-64, enable 32-bit syscalls with `ia32_emulation` where required. Steam moves from Non-OSS to Flatpak and needs `grub2-compat-ia32` plus a reboot; SELinux installations may also need `selinux-policy-targeted-gaming`. The packaged Wine 10.10 is WoW64-only.

## Removed and deprecated packages

### Leap removals

Leap 15.6 removes `bbswitch`, `bumblebee`, `bumblebee-status`, and `primus`; use NVIDIA SUSE Prime. It also removes unmaintained Python RPMs including `python-Keras-Applications`, `python-Theano`, `python-pep517`, `python-pygeos`, `python-jupytext`, `python-moviepy`, `python-requests-html`, `python-torch`, and legacy pytest, Jupyter, Dephell, and Spyder plug-ins. Audit RPM dependencies.

Leap 16 removes `nscd`, WSL1 support, `criu`, and `compat-libpthread-nonshared`; move `crun` consumers to `runc`. HexChat is no longer packaged because its upstream is archived; use Polari or Flatpak. Leap 16 carries the final `nmap` release available under the formerly compatible license and plans a later replacement. The unsupported `mcphost` MCP agent—configured with no permissions by default—and `lklfuse` are included as previews; `lklfuse` lacks Btrfs support because it cannot mount multi-device filesystems.

### SLES 15 SP6 removals and migrations

Replace `docker-runc` with `runc`; remove dependencies on `timezone-java`, insecure `dpt_i2o`, `openmpi2`, and `openmpi3`. Audit cloud-image and automation dependencies on removed Public Cloud Module componentized Azure CLI packages, legacy Google agents and SDK, packaged Terraform providers, `WALinuxAgent`, and related deployment helpers.

PHP 7.4 and `numad` were scheduled for SP7 removal. Replace `sev-tool` with `sevctl` and `gnote` with `bijiben`. Ceph clients `ceph-common`, `libcephfs-devel`, `python3-ceph-common`, `python3-rbd`, and `python3-rgw` are removed in SP7; `intel-opencl` and `intel-graphics-compiler` move to Package Hub.

### SLES 16 removals

SLES 16 itself ships no Salt packages even though SUSE Multi-Linux Manager still uses Salt internally to manage it. WBEM management through SBLIM is removed without a direct replacement.

SLES 16 removes `hplip`, `ansible-9`, and `ansible-core-2.16`. Prometheus is also removed because its inclusion was accidental and unsupported.

## Technology preview and support boundaries

SLES 15 SP6's disabled-by-default Confidential Computing Module is a technical preview containing unsupported host, secure-VM, and remote-attestation tooling.

Package inclusion does not imply broad automation support: apply the Ansible support boundary above, and check platform-specific previews in [platforms.md](platforms.md) and virtualization boundaries in [virtualization-containers.md](virtualization-containers.md).
