---
name: fedora-knowledge-patch
description: Fedora Linux 44 compatibility. Use for Fedora Linux work.
license: MIT
version: "44"
metadata:
  author: Nevaberry
---

# Fedora Linux Knowledge Patch

Use this skill when changing Fedora provisioning, package installation, RPM
specs, installer automation, boot and image workflows, networking, security,
desktop configuration, containers, virtualization, or distribution-provided
application stacks.

Read the breaking-change sections first. Then open every indexed reference
whose topic overlaps the task; the references contain the complete operational
details and release-specific transitions.

## Reference index

| Reference | Topics |
| --- | --- |
| [packages-rpm-dnf.md](references/packages-rpm-dnf.md) | DNF5 and DNF4 state, automation, PackageKit, RPM 4.20 and 6, keys, signatures, macros, package layout, base-system paths |
| [installation-boot-images.md](references/installation-boot-images.md) | Anaconda, RDP and Kickstart, partitioning, boot loaders, initramfs, live media, FIPS installation, architecture changes |
| [networking-security-identity.md](references/networking-security-identity.md) | NetworkManager, firewalls, crypto policy, CA trust, SSSD, PAM, login records, Secure Boot, polkit |
| [atomic-cloud-containers.md](references/atomic-cloud-containers.md) | bootc, rpm-ostree, composefs, Atomic Desktops, CoreOS, IoT, Cloud images, OCI metadata, Podman and Netavark |
| [storage-databases-services.md](references/storage-databases-services.md) | VDO, Stratis, Redis and Valkey, PostgreSQL, MySQL, MariaDB, directory, mail, web, and application servers |
| [languages-toolchains-packaging.md](references/languages-toolchains-packaging.md) | Language runtimes, compilers, build tools, RPM language macros, dependency transitions, Fedora packaging workflows |
| [desktop-hardware-apps.md](references/desktop-hardware-apps.md) | Wayland desktops, display and power management, input, multimedia, GPUs, printing, desktop applications |
| [orchestration-virtualization-observability.md](references/orchestration-virtualization-observability.md) | Kubernetes, Helm, libvirt, confidential guests, QEMU, eBPF, Koji, Packit, debuginfo verification, runtime monitors |

## Breaking changes quick reference

### Use DNF5 state consistently

`dnf` and `yum` invoke DNF5. Use `dnf4` or `dnf-3` only for a plugin or
workflow that has not been ported, and do not alternate implementations for
system transactions: transaction history and installed-package reasons are
separate after DNF5's one-time import.

Replace `dnf-automatic` with `dnf5-plugin-automatic`. Use the DNF5 Actions
plugin for transaction hooks previously handled by the Snapper plugin.

### Replace removed networking interfaces

Do not create or manage ifcfg files under
`/etc/sysconfig/network-scripts`. NetworkManager accepts native keyfiles, and
the legacy `network-scripts` package, `network.service`, `ifup`, and `ifdown`
are gone. Use `nmcli` or systemd-networkd interfaces.

Discover predictable interface names in Fedora Cloud rather than assuming
`eth0`. Do not expect Anaconda to create a NetworkManager profile for a wired
device that the installer did not configure.

### Treat image-mode systems as deployments

On a booted Atomic, CoreOS, or IoT system, do not expect DNF to mutate the
deployment. Use `rpm-ostree` or `bootc` as appropriate. composefs makes the
deployed root genuinely read-only, and CoreOS updates are delivered as OCI
images.

Atomic images do not guarantee FUSE 2, legacy `.pkla` polkit rules, or the old
Sericea and Onyx image names. Use `sway-atomic` and `budgie-atomic` for those
image families.

### Prepare explicitly for Podman 6

Before installing Podman 6, upgrade through Podman 5.8 and reboot so BoltDB
state migrates to SQLite. Ensure the host uses cgroups v2 and move rootless
networking from slirp4netns to Pasta with Netavark.

Netavark no longer supports iptables in Podman 6. Migrate custom container
firewall integration to nftables and review remote-client `containers.conf`
and `storage.conf` ownership and parsing.

### Account for RPM 6 without assuming v6 packages

Fedora's RPM 6 still builds v4 packages by default. Opt into v6 only for
deliberate testing with `_rpmformat 6`; v3 packages can be queried or unpacked
but not installed.

Use full fingerprints for RPM keys. `rpmsign --addsign` preserves existing
signatures and `--resign` replaces them. Stop using removed ID switches,
`rpmbuild --nodirtokens`, `brp-elfperms`, or custom `%__gpg_sign_cmd`
overrides. Treat scriptlet and trigger failures as transaction failures.

### Migrate security and identity assumptions

The default crypto policy rejects creating and verifying SHA-1 signatures.
Use a weaker compatibility policy only as a scoped, temporary bridge.

Create FIPS systems at installation or image-build time; do not depend on the
removed `fips-mode-setup` post-install conversion. Let TLS libraries discover
their trust store or use
`/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`, because the legacy CA
bundle paths are removed.

Do not assume the main SSSD daemon is privileged, use `sss_ssh_knownhosts`
instead of `sss_ssh_knownhostsproxy`, replace `pam_ssh_agent_auth`, and update
direct login-database integrations for `lastlog2` and `pam_lastlog2`.

### Update installer and boot automation

Use Anaconda's web interface and RDP boot options for remote graphical
installation; the VNC interfaces are removed. Expect GPT broadly, including
for x86 UEFI, and reserve 2 GiB for the default `/boot` layout.

Support EROFS when inspecting live media and zstd when handling dracut
initramfs images. Do not assume GRUB and shim RPM transactions write boot
partitions directly; boot-loader updates are moving to a unified updater.

### Audit distribution package migrations

Use Valkey names instead of relying indefinitely on `valkey-compat`. Select
versioned Kubernetes and CRI packages explicitly. Plan major migrations for
PostgreSQL, MySQL or MariaDB, Dovecot, 389 Directory Server, Tomcat, Django,
Ruby, Tcl/Tk, CMake, LLVM, Java, Node.js, and Ansible before a system upgrade.

Do not assume Java library RPMs install a runtime. Do not request removed
`community-mysql*`, `python-nose`, Python 3.8, old Fedora OpenJDK, deprecated
GTK Rust binding, or LibreOffice KF5 packages.

## Common new workflows

### Switch a bootc deployment

```console
sudo bootc switch quay.io/fedora/fedora-iot
```

Use DNF during container-image construction; use the deployment-aware tooling
after booting the image.

### Keep Helm 3 automation working

The unversioned `helm` command is Helm 4. Install the parallel compatibility
command when workflows still require Helm 3:

```console
sudo dnf install helm3
helm3 version
```

### Build modern Fedora packages

Expect `%cmake` to generate Ninja builds. Use `%pyproject` macros rather than
legacy Python `setup.py` macros, Fedora's Go vendor tooling for Go
applications, and the standardized R macros for R packages. Extend Fedora's
compiler flags with `_pkg_extra_*flags` instead of replacing the defaults.

RPM can consume packaged `sysusers.d` metadata directly, preserve static
library debuginfo, and hardlink identical files under `/usr`; write package
checks that tolerate shared inodes.

### Select parallel toolchain streams deliberately

Compatibility and parallel packages are part of several migrations: LLVM,
Tcl/Tk, Maven, Django, MySQL, MariaDB, Kubernetes, Helm, Node.js, and some Java
stacks. Depend on the exact package and executable required by the workload;
do not infer it from an unversioned command or from a library dependency.

### Use current storage and confidential-computing features

Manage dm-vdo through LVM2 and verify migration requirements before converting
kvdo volumes. Use Stratis token slots when a pool has multiple encryption
bindings, and remember that a scheduled snapshot revert occurs only when the
pool next starts.

On supported hardware, Fedora virtualization hosts can run AMD SEV-SNP and
Intel TDX confidential guests. Validate firmware, kernel, QEMU, and libvirt
support together rather than treating the guest definition alone as enough.

## Working method

1. Identify whether the target is package-mode, image-mode, live media, a
   container build, or a Fedora-hosted service.
2. Open the relevant references from the index before choosing package names,
   commands, paths, defaults, or compatibility packages.
3. Prefer native current interfaces; use compatibility packages and weakened
   policies only when a migration requirement justifies them.
4. For upgrades, inspect existing state before changing packages: DNF history,
   Podman database backend, disk labels, encryption bindings, database major
   versions, network profiles, and authentication policy can all require
   staged migration.
5. Test automation non-interactively and verify exit status. New DNF key
   handling, stricter Ansible templating, and RPM scriptlet error propagation
   can expose workflows that previously appeared successful.
