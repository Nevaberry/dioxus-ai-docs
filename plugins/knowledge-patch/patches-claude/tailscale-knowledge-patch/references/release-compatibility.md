# Release Compatibility and Upgrade Boundaries

Use this reference before selecting an artifact, advancing a stable deployment,
or applying a platform support policy.

## Stable and non-stable release boundaries

- The Android 1.82.0 client was delayed to 1.82.1. Versions 1.82.1 and 1.82.4
  are Android-only, while 1.82.2 and 1.82.3 were internal-only releases.
- Version 1.86.0 was halted on macOS on July 25, 2025 and on all platforms on
  July 28 because of regressions. Versions 1.86.1 and 1.86.3 were internal-only.
  Version 1.86.2 fixes a macOS state-file read failure that could require device
  re-approval. Version 1.86.4 fixes a fresh-install crash in the Standalone
  macOS client when `EncryptState` is enabled.
- Version 1.88.0 was internal-only.
- Version 1.90.0 was a release candidate for testing; 1.90.1 is its stable
  release.
- Version 1.92.0 was a release candidate for testing; 1.92.1 is its stable
  release.
- Version 1.94.0 was a release candidate for testing; 1.94.1 is its stable
  release.
- Versions 1.96.0 and 1.96.1 were release candidates for testing; 1.96.2 is
  their stable release.
- Version 1.98.0 was a release candidate for testing. The Linux 1.98.1 release
  was withdrawn because of a MagicDNS interaction regression pending a fix.

## Platform floors and package availability

### macOS minimum version (since 1.88.1)

macOS 12 is the minimum supported version.

### QNAP packages (since 1.88.1)

QNAP builds resumed through manual packages-site downloads, with later
availability through QNAP App Center.

### Windows signing certificate (since 1.84.0)

Windows 1.84.2 uses a new code-signing certificate. Its subject and issuer are
unchanged, but its serial number differs; update deployments that allowlist the
certificate by serial number.

## Corrective stable-line behavior

The 1.86 stable line fixes a CSRF issue that could cause web-interface login
failures and restores hostname verification when the control-plane connection
uses a CONNECT HTTPS proxy. It also improves proxy auto-detection and PAC
handling on Windows 10 version 1607 and earlier.
