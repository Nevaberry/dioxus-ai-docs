# Upgrade, Security, and Platform Boundaries

## Unsupported release and container base (`1.9.0`)

OpenTofu 1.6 is unsupported and receives no further security updates; upgrade
to at least the 1.7 series.

Using `ghcr.io/opentofu/opentofu` as the base for a custom image was deprecated
in 1.9 and is unsupported from `1.10.0`. Custom images must use another base
rather than depending on the OpenTofu image as a build foundation.

## Operating-system boundaries (`1.10.0`)

OpenTofu requires Linux kernel 3.2+ or macOS 11+. On Windows, junctions are no
longer treated as symlinks. A `TEMP` path that traverses a junction can fail;
use a real directory symlink or a path containing neither mechanism.

## PostgreSQL mixed-version hazard (`1.10.0`)

Do not allow OpenTofu 1.10-or-newer and older processes to share a PostgreSQL
backend database. Their locking implementations are incompatible and can admit
conflicting state writes, causing data loss.

## Platform and transport hardening (`1.11.0`)

OpenTofu 1.11 requires macOS 12 Monterey or newer. It rejects SHA-1 signatures
during TLS handshakes and rejects malformed SSH certificates whose signing key
is itself a certificate key.

Use 1.11.4+ when provider or module installation can encounter untrusted ZIP
archives. Earlier 1.11 releases can spend excessive time processing a malicious
archive.

## AzureRM backend upgrade (`1.11.0`)

The AzureRM backend ignores deprecated `endpoint`/`ARM_ENDPOINT` and
`msi_endpoint`/`ARM_MSI_ENDPOINT`. Replace the latter with `MSI_ENDPOINT`, avoid
combining `environment` with `metadata_host`, and run
`tofu init -reconfigure`. Do not use `-migrate-state`, because this change does
not move state.

## S3 module credential selection (`1.11.0`)

S3 module sources use AWS CLI/SDK credential discovery. Test credential
selection during the upgrade: standard precedence can choose a different
source than the former custom sequence. The new behavior also supports IAM
roles for service accounts and related SDK schemes.

## Provisioner and package deprecations (`1.12.0`)

WinRM connections still work but warn, and are planned to become errors in
1.13. Migrate Windows provisioners to SSH. The 1.12 series is the last planned
series for macOS 12. Official 32-bit `386` and `arm` packages continue through
1.13 but are planned for later removal; `amd64` and `arm64` are unaffected.

## Early 1.12 security floor (`1.12.0`)

Early 1.12 releases had defects involving SSH connections, OpenBao-wrapped
state-encryption data, revoked SSH CA keys, and malicious Git URLs that could
read arbitrary files. The original patch floor for those issues was 1.12.4.
That floor is superseded by the newer registry security fixes below; use 1.12.6
or later in the 1.12 series.

## OCI redirect credential disclosure (`1.11.14-1.12.6-security`)

Upgrade to OpenTofu 1.12.6 or 1.11.14 before installing modules or providers
from OCI Distribution registries. Earlier versions can resend credentials
intended for the original registry origin to the destination of an HTTP
redirect.

## Crafted relative-URL resource exhaustion (`1.11.14-1.12.6-security`)

An attacker-controlled remote-state backend or provider/module registry can
make earlier releases consume excessive CPU or memory during `tofu init` by
returning crafted relative URLs. OpenTofu 1.12.6 and 1.11.14 fix this
initialization-time denial-of-service issue.

## Final 1.11 patch (`1.11.14-1.12.6-security`)

OpenTofu 1.11.14 is the final patch planned for the 1.11 series. Move
installations that must temporarily take that fix to a newer release series as
soon as possible.
