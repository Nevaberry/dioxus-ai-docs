# Installation, Migration, and Lifecycle

## Leap upgrades and lifecycle

For Leap 15.6, install lifecycle metadata and identify installed packages that
are no longer maintained or are scheduled for removal:

```sh
zypper install lifecycle-data-openSUSE
zypper lifecycle
```

Leap 15.5 changed the RPM/repository signing key from 2048-bit to 4096-bit RSA,
after maintenance introduced it to 15.4. An upgrade from an older unpatched
release may need the new key imported manually before repositories are trusted.

Leap 16 plans annual minor releases with 24 months of community maintenance per
release. The supported path from 15.6 uses its migration tool:

```sh
zypper in opensuse-migration-tool
```

The same tool can also migrate to Slowroll, Tumbleweed, or SLES. The provisional
Leap 16 series plan runs through 16.6 in 2031, with a successor expected in 2032;
Leap Micro follows the same schedule. Leap 16 is intended to be safe past the
2038 timestamp rollover and is source- and binary-identical with SLES 16 for
workload development and later enterprise deployment. (leap-16.0)

## SLES service-pack upgrades and lifecycle

Before an SLES 15 SP6 upgrade, run `zypper patch`; only the latest source patch
level is supported. Without LTSS, reach SP5 before SP6. Service-pack skipping is
supported only with an LTSS contract.

SLE for HPC is no longer separate. HPC 15 SP3-SP5 migrates to SLES 15 SP6 while
retaining enabled modules. Enable Server Applications, Web and Scripting, HPC,
Desktop Applications, and Development Tools; start from Text Mode or Minimal
System because former HPC roles are gone, then explicitly select `slurm`,
`slurm-node`, `patterns-hpc-libraries`, and other needed components.

SLES 15 SP7 and SLES 16.0 are fully maintained through 2034-07-31. LTSS can add
12-36 months in yearly increments, through December 2037. SLES 16's final minor,
16.6, is planned for 48 months of general support ending in November 2035, with
LTS and Extreme LTS extending beyond 2040. SLES for SAP Applications 16 instead
has two years of general support followed by three years of extended support.

## Agama installation and automation

Agama replaces the deprecated YaST installer in Leap 16. It provides minimal
network-install, full-repository, and remote PXE-client media, plus Web, CLI, and
HTTP API front ends for unattended deployments.

AutoYaST profiles have substantial schema compatibility but are not drop-in
Agama configurations. Agama also supports JSON/Jsonnet schemas, repeated imports,
and automated profile generation and validation. Validate generated profiles
before installation. The later SLES 16.0 revision permits SSH public keys for
every installer-created account. (16.0-rev-2026-08-04)

Agama installation images have no separate rescue system. Recover through
another virtual console as `root`, open a terminal in the installation image, or
append `3` to the kernel command line for runlevel 3.

The installer UI edits only existing NetworkManager connections. Use Agama CLI
or configuration to create a connection for an unconfigured device.

Use `rd.ntp=<server>` to synchronize time before Agama starts, particularly for
certificate validation and logs. Agama also has an `ntp` profile section;
imported AutoYaST `ntp-client` settings convert to it and persist on the target:

```text
rd.ntp=ntp.example.com
```

## SLES 16 distribution migration

The Distribution Migration System replaces Unified Installer. `run_migration`
reboots into a live image for preflight, a network Zypper upgrade, boot-loader
finalization, and optional post-migration tasks. Migration while the source
continues running is unsupported. SLES 16.0 accepts only SLE 15 SP7 as a source,
with incomplete coverage; broader coverage is deferred to 16.1.

SLES 16.0 clients can register to RMT, but RMT itself must run on SLE 15;
SLES 16 hosting is expected with 16.1.

SLES 16 removes the SLE 15 module model and separate pool/update channels. Each
minor still has its own repositories, so minor-release transitions remain
necessary. Transactional updates are unsupported; use SLE Micro for that model.

The migration tool rewrites obsolete SAP Host Agent PAM module names
`pam_unix_auth.so`, `pam_unix_acct.so`, `pam_unix_session.so`, and
`pam_unix_passwd.so` under `/etc/pam.d/` to `pam_unix.so` because the old links
no longer exist.

## Installation network and storage behavior

Allow `installer-updates.suse.com`, which replaces `updates.suse.com` for SLES
15 SP6 installer self-updates.

The SLES 15 SP6 installer no longer reuses an existing LVM layout. LUKS2 is fully
supported in YaST Partitioner, including AutoYaST partitioning profiles.

SLES 16 netboot rejects `install=`. Use:

```text
root=live:<installer-image-URL> inst.install_url=<installation-repository-URL>
```

SLES 16 uses GRUB 2.12, not BLS or `systemd-boot`. PCR-based disk unlocking on
AMD64/Intel 64 requires TPM 2.1 or later.

Zypper supports parallel downloads on Leap 16. Use `zypper search-packages` to
search enabled and disabled SLE modules through SCC or RMT:

```sh
zypper search-packages SEARCH_TERM
```
