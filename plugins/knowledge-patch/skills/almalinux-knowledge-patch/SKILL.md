---
name: almalinux-knowledge-patch
description: AlmaLinux 10.2 compatibility. Use for AlmaLinux work.
license: MIT
version: "10.2"
metadata:
  author: Nevaberry
---

# AlmaLinux Knowledge Patch

Baseline: AlmaLinux 9.3. Covered range: versioned changes from 9.4 through
10.2, including `9.8-10.2-ga`, plus lifecycle, ELevate, and project-security
updates captured through 2026-07-11.

## Reference index

| Reference | Topics |
| --- | --- |
| [platform-installation.md](references/platform-installation.md) | Kernels, architectures, x86-64-v2, i686, media, Btrfs, Secure Boot, legacy hardware, lifecycle |
| [packages-toolchains.md](references/packages-toolchains.md) | Application streams, compilers, debugging tools, package omissions and replacements |
| [security-cryptography.md](references/security-cryptography.md) | Crypto policies, OpenSSL, RPMv6, OpenPGPv6, SELinux, Keylime, identity |
| [operations-virtualization.md](references/operations-virtualization.md) | Networking, logging, containers, IBM POWER KVM, SPICE, kernel behavior |
| [system-upgrades.md](references/system-upgrades.md) | Beta conversion, ELevate paths, Leapp contracts, third-party repository transitions |
| [security-advisories.md](references/security-advisories.md) | 2026 kernel, container-escape, local-root, and nginx advisories |

## Compatibility breaks and deprecations

### Choose the AlmaLinux 10 x86 build deliberately

The standard AlmaLinux 10 `x86_64` build uses the x86-64-v3 CPU baseline.
Use AlmaLinux's `x86_64_v2` build for older CPUs, but account for the fact
that RHEL 10 third-party packages target v3. A v2 system is safest with the
default OS package set or packages rebuilt for v2 (`10.0`).

AlmaLinux 10.0 removed i686 packages. AlmaLinux 10.2 restores i686
userspace for legacy applications, CI, and containers
(`9.8-10.2-ga`), but it does not add an i686 installer or 32-bit kernel.
The packages live on `vault.almalinux.org`, official containers use
`linux/386`, and the stream is maintained through 2035 (`10.2`).

### Do not assume upstream package parity

Notable packages absent from AlmaLinux include:

- `9.5`: `insights-client`, `kmod-redhat-*`, `kpatch*`,
  `openssl-fips-provider`, `rhc`, Subscription Manager add-ons,
  `virt-who`, `virtio-win`, and Windows SPICE packages.
- `9.6`: `command-line-assistant`.
- `10.0`: `redhat-cloud-client-configuration`,
  `redhat-flatpak-data`, `redhat-support-lib-python`, and
  `redhat-support-tool`.

AlmaLinux supplies its own backgrounds, index, logos, release, and related
branding packages (`9.7`). See the package reference for exact names.

### Toolchain and lifecycle traps

- Starting with GCC Toolset 15, the toolset no longer ships Annobin or
  `dwz` (`9.7`). System Annobin remains separately versioned.
- A minor AlmaLinux release reaches end of life when the next minor ships.
  The major version's active and security windows do not extend an old minor
  (`release-catalog`).
- New AlmaLinux 10.1 installations enable CRB by default (`10.1`). Do not
  assume an upgraded or older installation has the same repository state.

## Upgrade hazards

Stable ELevate supports AlmaLinux 9.8 to 10.2
(`elevate-upgrades`). The `x86_64_v2` AlmaLinux 9 to AlmaLinux 10 and
Kitten 10 paths use dedicated `leapp-data-*x86_64_v2` packages and were
released to NG.

Before chaining CentOS 7 to EL8 to EL9, remove every ELevate-related EL7
package after reaching EL8. Stale `leapp-data-*` can conflict with
`leapp-upgrade-*` under `/etc/leapp/repos.d/system_upgrade` and create
malformed semicolon-suffixed symlinks.

Keep these rules in mind:

- `--target` selects only a published, supported destination minor; an
  unreleased target may disappear until it ships.
- Non-`x86_64` architectures can use the standard quickstart with current
  map files.
- EL9-to-EL10 PES data covers EPEL, Docker CE, PostgreSQL, nginx,
  KernelCare, MariaDB, Imunify, and Imunify360 alt-PHP, but not MariaDB
  MaxScale or Tools.
- Microsoft signing keys differ: `BE1229CF` for EL8/EL9 and `F748182B`
  for EL10.
- Imunify360 alt-PHP needs its repository token substituted before upgrade.
- LUKS volumes bound to Clevis with a TPM 2.0 token are now permitted.
- `net.naming-scheme` is enabled by default.
- `--enable-experimental-feature` explicitly enables experimental Leapp
  features, including simplified LiveMode.

Use [system-upgrades.md](references/system-upgrades.md) for the exact
Leapp/data versions, repository mappings, transition actions, and 9.4 or 10.0
beta-to-stable commands.

## Installation and storage quick reference

### AlmaLinux 10 media

Media follow `AlmaLinux-10.0-$arch-{boot,minimal,dvd}.iso`. Only boot media
needs a network source. If discovery fails, use a mirror's
`10.0/BaseOS/$arch/kickstart/` path (`10.0`).

Verify with the AlmaLinux 10 signing key:

~~~console
wget https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-10
gpg --import RPM-GPG-KEY-AlmaLinux-10
gpg --verify CHECKSUM
sha256sum AlmaLinux-10.0-$(uname -m)-boot.iso
~~~

The key fingerprint is
`EE6D B7B9 8F5B F5ED D9DA 0DE5 DEE5 C11C C2A1 E572`.

### Storage, boot, and hardware

- AlmaLinux 10.1 can install and boot on Btrfs. Initial scope is the installer
  and storage-management stack, not blanket support across all software
  (`10.1`).
- AlmaLinux 9.8 shim 16.1 is dual-signed with the Microsoft 2011 and 2023
  UEFI Secure Boot certificates (`9.8`).
- AlmaLinux 9.4 and 10.2 restore support for substantial sets of older
  storage and networking hardware. Some 9.4 `be2net` devices need kernel
  `5.14.0-427.18.1.el9_4` or later.

## Cryptography and trust quick reference

| Release | Behavior |
| --- | --- |
| AlmaLinux 9.5 | System crypto-policy algorithm selection extends to Java; OpenSSL 3.2.2 adds TLS certificate compression and TLS 1.3 Brainpool curves. |
| AlmaLinux 9.7 | Select the `PQ` subpolicy to enable post-quantum algorithms; OpenSSL 3.5 adds ML-KEM, ML-DSA, SLH-DSA, and default hybrid ML-KEM TLS groups. |
| AlmaLinux 10.0 | Crypto policies, OpenSSL, and OpenSSH 9.9 support post-quantum algorithms; OpenSSL adds FIPS-compliant PKCS #12 and `pkcs11-provider`. |
| AlmaLinux 10.1 | Post-quantum algorithms are on by default in every system crypto policy; RPMv6 supports multiple signatures and Sequoia handles post-quantum RPM and OpenPGPv6 signatures. |

Other high-value security changes:

- OpenSSL provider configuration has a drop-in directory (`9.4`).
- SELinux 3.6 supports explicit deny rules (`9.4`); SELinux 3.8 can emit CIL
  from `audit2allow` and supports the sandbox on Wayland (`10.0`).
- Keylime agent 0.2.7 supports IDevID and IAK credentials and defaults to
  TLS 1.3; `keylime-policy` consolidates policy management (`10.0`).
- AlmaLinux 10.0 supplies a `sudo` system role for fleet configuration.

## Applications, tracing, and virtualization

- AlmaLinux 9.4 adds Python 3.12, Ruby 3.3, PHP 8.2, nginx 1.24,
  MariaDB 10.11, and PostgreSQL 16 streams.
- AlmaLinux 9.6 updates Maven 3.9, MySQL 8.4, nginx 1.26, and PHP 8.3.
- AlmaLinux 9.8 adds Python 3.14 and new MariaDB, PostgreSQL, and Ruby
  streams; AlmaLinux 10.2 includes Python 3.14, PostgreSQL 18, MariaDB 11.8,
  Ruby 4.0, and PHP 8.4 (`9.8-10.2-ga`).
- AlmaLinux 10 enables frame pointers distribution-wide for real-time tracing
  without rebuilding workloads (`10.0`).
- IBM Power KVM starts as a technology preview in 9.6 and is fully enabled
  for IBM POWER in 10.2.
- AlmaLinux 10 enables SPICE in server and client applications (`10.0`).
- The AlmaLinux 9.8 kernel includes a dentry-lock race fix for excessive
  `systemd` and `ps` CPU during task cleanup (`9.8`).

Use the package and operations references for complete version matrices.

## Security response snapshot

Advisory status here is from `project-news` on 2026-07-11. Re-check current
repositories before acting.

| Issue | Exposure | Snapshot status |
| --- | --- | --- |
| GhostLock, CVE-2026-43499 | Local root and container escape; every supported release | Patched kernels in testing |
| Januscape, CVE-2026-53359 | KVM/x86 guest-to-host root escape; every release | Patched kernels in testing |
| Bad Epoll, CVE-2026-46242 | Local root on AlmaLinux 9 and 10 | Patched kernels in testing |
| IPv6 fragmentation flaw | Container-to-host root on AlmaLinux 10 and Kitten 10 | AlmaLinux 10 fix in testing; Kitten fix scheduled |
| CIFSwitch, CVE-2026-46243 | Local root through `cifs.spnego` under specific namespace/package conditions | Fixed kernels in production; update and reboot |
| CVE-2026-46333 | Read root-owned files through `__ptrace_may_access()` | Patched kernels in testing; mitigation available |
| NGINX Rift, CVE-2026-42945 | Unauthenticated rewrite-module heap overflow | Fixed packages in production for all supported releases and streams |

Copy Fail, Dirty Frag, and Fragnesia are additional local-root risks for
multi-tenant systems, build farms, CI, and untrusted shells. Read
[security-advisories.md](references/security-advisories.md) for CVEs,
affected contexts, mitigations, and captured package state.
