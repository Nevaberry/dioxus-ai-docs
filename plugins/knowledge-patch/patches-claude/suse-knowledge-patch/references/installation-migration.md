# Installation, Migration, and Lifecycle

## openSUSE Leap upgrades

### Signing key on older upgrades (`leap-15.6`)

Leap 15.5 changed the RPM and repository key from 2048-bit to 4096-bit RSA and
introduced it to 15.4 through maintenance. A system upgrading from an older
release that never received that maintenance must import the key manually
before repositories can be trusted.

### Supported migration from Leap 15.6 (`leap-16.0-guide`)

Use the migration tool shipped for the source release:

```sh
zypper in opensuse-migration-tool
```

Leap 16 minor releases are planned annually with 24 months of community
maintenance. The provisional series plan continues through Leap 16.6 in 2031,
with a successor expected in 2032; Leap Micro is adopting the same schedule.

### Agama and migration targets (`leap-16.0`)

Agama replaces the deprecated YaST-based installer. The openSUSE Migration Tool
can upgrade Leap 15 to Leap 16 and can also migrate a system to Slowroll,
Tumbleweed, or SLES.

Leap 16 is source- and binary-identical with SLES 16, so workloads can be built
and tested on Leap for later SLES deployment. Zypper can download packages in
parallel. Leap is 2038-safe.

## SLES 15 service-pack upgrades

### SP6 prerequisites and HPC product migration

Patch to the latest level with `zypper patch` before upgrading. Without LTSS,
upgrade to SLE 15 SP5 before SP6; skipping service packs is supported only by
an LTSS contract.

SLE for HPC is no longer a separate product. HPC 15 SP3–SP5 systems migrate to
SLES 15 SP6 and retain enabled modules. Enable Server Applications, Web and
Scripting, HPC, Desktop Applications, and Development Tools for an HPC system.
The former HPC roles are gone: start from Text Mode or Minimal System and add
`slurm`, `slurm-node`, `patterns-hpc-libraries`, and other required components.

### Installer self-update and storage behavior

Allow `installer-updates.suse.com`; installation media no longer contacts
`updates.suse.com` for self-updates. The installer no longer tries to reuse an
existing LVM layout. LUKS2 is fully supported in the YaST Partitioner and in
AutoYaST partitioning profiles rather than remaining a technology preview.

### SP7 and SLES 16.0 horizons

SLES 15 SP7 and SLES 16.0 are each fully maintained through 2034-07-31. LTSS
can add 12–36 months in yearly increments, as late as December 2037.

## SLES 16 lifecycle and migration

### Product support extensions

SLES 16.6, the final minor release, gets 48 months of general support, expected
to end in November 2035; LTS and Extreme LTS can extend support beyond 2040.
SLES for SAP Applications 16 instead receives two years of general support and
three years of extended support.

### Agama media and automation

Agama is available as minimal network-install, full-repository, and remote
PXE-client media. It exposes Web, CLI, and HTTP API front ends for unattended
deployment. AutoYaST profiles have substantial schema compatibility but are not
drop-in configurations. Native input uses JSON/Jsonnet and permits repeated
configuration imports.

The `16.0-rev-2026-08-04` revision adds automated profile generation and
validation. Validate generated profiles before installation.

### Recovery without a rescue image

Agama media has no separate rescue system. Use another virtual console and log
in as `root`, open a terminal from the installation image, or append `3` to the
kernel command line to boot directly to runlevel 3.

### RMT host limitation

SLES 16.0 clients can register against RMT, but RMT itself must run on SLE 15.
Hosting RMT on SLES 16 is expected with 16.1.

### Distribution Migration System

The Distribution Migration System replaces the Unified Installer.
`run_migration` reboots into a live image, performs preflight, a network-based
Zypper upgrade, boot-loader finalization, and optional post-migration work.
Migrating while the source system remains running is unsupported. SLES 16.0
accepts only SLE 15 SP7 as a source and has incomplete migration coverage;
broader source support is deferred to 16.1.

### Boot-loader boundaries and update model

SLES 16.0 ships GRUB 2.12 and uses neither BLS nor `systemd-boot`. PCR-based
full-disk unlocking on AMD64/Intel 64 requires TPM 2.1 or newer.

Transactional updates are unsupported on SLES 16; use SUSE Linux Enterprise
Micro for that update model.

### Repository model

SLE 15 modules and separate pool/update channels are removed. Every SLES 16
minor still has separate repositories, so repository transitions remain
necessary between minor releases.

## SLES 16 installation details

### Netboot parameters

`install=` is no longer accepted. Use:

```text
root=live:<installer-image-URL> inst.install_url=<installation-repository-URL>
```

Architecture-specific IBM Z `parmfile` rules differ; see
[platforms.md](platforms.md).

### NetworkManager connections in Agama

The installer UI edits only existing NetworkManager connections. Create a
connection for an unconfigured device with Agama CLI or a configuration file.

### Early time synchronization

Use `rd.ntp=<server>` to synchronize time before Agama starts, which helps
certificate validation and installer logging:

```text
rd.ntp=ntp.example.com
```

Agama also has a native `ntp` profile section. Imported AutoYaST `ntp-client`
settings are converted to that section and persisted on the target.

### Installer-created SSH keys

The `16.0-rev-2026-08-04` revision permits SSH public keys for every account
created during installation, not only a limited account type.
