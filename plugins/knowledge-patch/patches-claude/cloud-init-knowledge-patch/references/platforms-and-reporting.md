# Platforms and Reporting

Use this reference for distribution-specific behavior, platform discovery,
image defaults, and reporting consumers.

## Distribution modules and preserved configuration

### Rocky Linux

The `ca_certs` module supports Rocky Linux (26.1). Images can manage trusted CA
certificates through cloud-init instead of carrying distribution-specific
bootstrap logic for that task.

### openEuler

`cc_rh_subscription` no longer handles openEuler (26.1). Remove conditionals
that route openEuler through that module and do not interpret its absence as a
transient detection problem.

### RHEL

Cloud-init does not overwrite local changes in
`disable-sshd-keygen-if-cloud-init-active.conf` (26.1). Preserve administrator
edits; packaging and image assembly must not restore the older overwrite
behavior.

## Distribution support and defaults

### Amazon Linux modules

Amazon Linux supports `yum_add_repo` and `ca_certs` (26.2). Images can configure
Yum repositories and trusted CA certificates through cloud-config modules
instead of separate bootstrapping.

When removing old bootstrap logic, verify ordering so repositories and trust
material are available before dependent package operations.

### Azure Linux 4.0

Azure Linux 4.0 is supported (26.2). Recheck local distribution-detection or
compatibility patches before carrying them into current images.

### Alpine APK mirror

Alpine uses its CDN as the default APK mirror (26.2). Do not restore an older
mirror implicitly; set a different mirror only when image policy requires it.

### Debian Bullseye backports

Debian's backports suite selection is updated for Bullseye (26.2). Allow
cloud-init to use the current suite behavior and remove workarounds that force
the former selection.

## Platform detection

### Tilaa and s390x LXD

Cloud-init detects the Tilaa cloud platform and s390x LXD environments (26.1).
Before retaining local detection workarounds, test whether built-in detection
already covers the target.

### CloudStack virtual-router discovery

CloudStack can obtain virtual-router information from NetworkManager leases
(26.2). Keep lease data available to discovery and do not assume information
must come from only an older lease source.

When diagnosis fails, confirm that NetworkManager produced a usable lease and
that image cleanup did not remove it before cloud-init discovery.

### Oracle iSCSI root discovery

On Oracle, dracut images can detect an iSCSI root through iBFT (26.2). Preserve
iBFT information through early boot and check the dracut path before adding a
manual iSCSI-root override.

## Raspberry Pi

Raspberry Pi support includes these behaviors (26.1):

- keymap handling;
- USB-gadget handling; and
- a systemd network service template.

For Raspberry Pi, cloud-init also:

- disables fallback network configuration; and
- removes APT mirror configuration.

These are platform defaults. When an image does not emit generic fallback
networking or APT mirror configuration, inspect platform behavior before adding
a generic workaround that would reverse it.

Image tests should cover keymap application, the intended USB-gadget behavior,
activation of the systemd network template, and the deliberate absence of the
generic networking and mirror configuration.

## Reporting

Reporting finish events include their duration (26.1). Consumers can obtain
stage timing directly from the finish event rather than reconstructing it from
separate timestamps.

When changing an integration, retain duration through:

1. event parsing;
2. internal storage;
3. serialization or export; and
4. downstream display and alerting.

Treat duration as part of the finish-event payload and test consumers with the
field present.
