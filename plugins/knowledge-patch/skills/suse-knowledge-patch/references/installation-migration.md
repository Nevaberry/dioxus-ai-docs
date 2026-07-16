# Installation, Migration, and Lifecycle

Use this reference for upgrade eligibility, Agama deployment, boot parameters, recovery, repository transitions, and support horizons.

## Contents

- [Migration eligibility and lifecycle](#migration-eligibility-and-lifecycle)
- [Agama installation and automation](#agama-installation-and-automation)
- [Boot and installation parameters](#boot-and-installation-parameters)
- [Installation storage behavior](#installation-storage-behavior)
- [SAP migration compatibility](#sap-migration-compatibility)

Versioned batch attributions used across the merged references: `leap-15.6`, `leap-16.0-guide`, and `leap-16.0`.

## Migration eligibility and lifecycle

### Leap migration

Leap 16 plans annual minor releases with 24 months of community maintenance per release. The provisional plan continues through Leap 16.6 in 2031, expects a successor in 2032, and applies the same schedule to Leap Micro.

Use the migration tool shipped for Leap 15.6 for its supported Leap 16 path:

```sh
zypper in opensuse-migration-tool
```

The tool can also migrate to Slowroll, Tumbleweed, or SLES. Leap 16 provides source- and binary-identical workloads with SLES 16, allowing creation and testing on Leap before SLES deployment.

### SLES service-pack upgrades

Patch the source to its latest level with `zypper patch` before an SLES 15 SP6 upgrade:

```sh
zypper patch
```

Without LTSS, upgrade to SLE 15 SP5 before SP6. Skip service packs only when the LTSS contract supports that path.

SLE for HPC is no longer a separate product. Migrate HPC 15 SP3–SP5 to SLES 15 SP6 while retaining enabled modules. Start new HPC systems from Text Mode or Minimal System because the former HPC roles are gone; explicitly enable Server Applications, Web and Scripting, HPC, Desktop Applications, and Development Tools modules and select packages such as `slurm`, `slurm-node`, and `patterns-hpc-libraries`.

### SLES 16 Distribution Migration System

Use the Distribution Migration System instead of the former Unified Installer. `run_migration` reboots into a live migration image for preflight, a network-based Zypper upgrade, boot-loader finalization, and optional post-migration work. Migration while the source system remains running is unsupported.

SLES 16.0 accepts only SLE 15 SP7 as its source and has incomplete migration coverage; broader support is deferred to 16.1.

SLES 16.0 is fully maintained through 2034-07-31. LTSS can add 12–36 months in yearly increments, as late as December 2037. The final 16.6 minor release receives 48 months of general support, expected through November 2035; LTS and Extreme LTS can extend beyond 2040. SLES for SAP Applications 16 instead uses two years of general support followed by three years of extended support.

SLES 15 SP7 is fully maintained through 2034-07-31 and can likewise receive 12–36 months of LTSS through as late as December 2037.

### Update and repository model

SLES 16 does not support transactional updates; use SUSE Linux Enterprise Micro when that update model is required.

The SLE 15 module model and separate pool and update channels are removed. Each SLES 16 minor release still has distinct repositories, so perform repository transitions between minor releases.

SLES 16.0 clients can register against RMT, but host the RMT service itself on SLE 15. Hosting it on SLES 16 is expected only with 16.1.

## Agama installation and automation

### Installer model

Leap 16 and SLES 16 use Agama in place of the deprecated YaST installer. Agama media is available as a minimal network installer, a full repository image, or a remote PXE client. It exposes Web, CLI, and HTTP API front ends for unattended deployment.

AutoYaST profiles have substantial format and schema compatibility but are not drop-in replacements. Use Agama's JSON/Jsonnet schema when appropriate; repeated configuration imports are supported.

### Recovery

Agama installation images have no separate rescue system. Use another virtual console and log in as `root`, open a terminal from the installation environment, or append `3` to the kernel command line to boot directly into runlevel 3.

### Network connections and time

Agama's UI edits only existing NetworkManager connections. Create a connection for an unconfigured device with the CLI or a configuration file.

Use `rd.ntp=<server>` to synchronize time before Agama starts, particularly for certificate validation and accurate logs:

```text
rd.ntp=ntp.example.com
```

Agama also supports an `ntp` profile section. Imported AutoYaST `ntp-client` settings are converted into that section and persisted on the installed target.

### Installer self-update

SLES 15 SP6 installation media contacts `installer-updates.suse.com` instead of `updates.suse.com` for self-update. Permit the new hostname in installation firewalls and allowlists.

## Boot and installation parameters

### SLES netboot

SLES 16 rejects the former `install=` parameter. Use both `root=live:` and `inst.install_url=`:

```text
root=live:<installer-image-URL> inst.install_url=<installation-repository-URL>
```

### Boot-loader boundaries

SLES 16.0 ships GRUB 2.12 and uses neither BLS nor `systemd-boot`. On AMD64/Intel 64, PCR-based full-disk unlocking requires TPM 2.1 or later.

### Repository signing keys

Leap 15.5 changed RPM and repository signing from a 2048-bit to a 4096-bit RSA key after distributing the new key to 15.4 through maintenance. Before upgrading an older unpatched release, manually import the new key so repositories can be trusted.

## Installation storage behavior

The SLES 15 SP6 installer no longer attempts to reuse an existing LVM layout. LUKS2 is fully supported in the YaST Partitioner, including AutoYaST partitioning profiles.

## SAP migration compatibility

During migration, rewrite obsolete SAP Host Agent PAM module references in `/etc/pam.d/`—`pam_unix_auth.so`, `pam_unix_acct.so`, `pam_unix_session.so`, and `pam_unix_passwd.so`—to `pam_unix.so`. The migration tool performs this rewrite because the former compatibility links no longer exist.
