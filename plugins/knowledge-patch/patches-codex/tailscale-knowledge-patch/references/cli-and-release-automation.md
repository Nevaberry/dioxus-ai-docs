# CLI and Release Automation

## CLI compatibility

### Configuration commands (since 1.80.0)

`tailscale configure` and its subcommands are no longer alpha, except
`tailscale configure kubeconfig`. The Standalone macOS client also provides
these programmatic system-extension controls:

```console
tailscale configure sysext activate
tailscale configure sysext deactivate
tailscale configure sysext status
```

### Duplicate flags and containers (since 1.84.0)

Commands reject multiple occurrences of the same flag. Audit command builders
that combine defaults, user options, and environment variables. This parsing
change initially prevented container image 1.84.0 from setting `--accept-dns`
through `TS_EXTRA_ARGS`; image 1.84.2 restores that usage.

### Interactive confirmation (since 1.88.1)

Significant actions may prompt for `y/n` confirmation. An invocation that was
previously unattended may now wait for input, so test automation around each
affected command.

### Machine-readable DNS output (since 1.96.2)

Both DNS inspection commands accept `--json`:

```console
tailscale dns query example.internal --json
tailscale dns status --json
```

### Readiness and address assertions (since 1.96.2)

Use `tailscale wait [flags]` to wait until Tailscale resources are available
for binding. Use `tailscale ip --assert=<specific-ip-address>` to fail unless
the supplied address matches one of the node's Tailscale IP addresses.

```console
tailscale wait
tailscale ip --assert=100.64.0.1
```

### Release-candidate track (since 1.96.2)

The `release-candidate` track works with both version checks and updates:

```console
tailscale version --track=release-candidate
tailscale update --track=release-candidate
```

This lets automation inspect or install release-candidate builds without
confusing them with the stable track.

### Local inspection commands (since 1.102.2)

Use the dedicated commands rather than reconstructing local state:

```console
tailscale get
tailscale whoami
tailscale service list
```

They report the node's preferences, user and device identity, and visible
Tailscale Services. `tailscale status --peers=false` now also includes the
current device name.

## Automation integrations

### GitHub Action runners and caching (since 1.82.0)

The Tailscale GitHub Action is generally available on macOS and Windows
runners. Set `use-cache` to the string `'true'` to cache Tailscale binaries:

```yaml
with:
  use-cache: 'true'
```

## Release boundaries and rollout hazards

### Android 1.82 release line

Android 1.82.0 was delayed to 1.82.1. Versions 1.82.1 and 1.82.4 are
Android-only; 1.82.2 and 1.82.3 were internal-only. Do not infer equivalent
availability across platforms from these version numbers.

### Halted 1.86 rollout

The 1.86.0 rollout was halted for macOS on July 25, 2025, and for every
platform on July 28 because of regressions. Versions 1.86.1 and 1.86.3 were
internal-only. Version 1.86.2 fixes a macOS state-file read failure that could
require device re-approval. Version 1.86.4 fixes a fresh-install Standalone
macOS crash when `EncryptState` is enabled.

### Internal 1.88 build

Version 1.88.0 was internal-only. Use 1.88.1 when referring to the stable
client line.

### Stable release boundaries

- 1.90.0 was a release candidate intended only for testing; 1.90.1 is stable.
- 1.92.0 was a release candidate intended only for testing; 1.92.1 is stable.
- 1.94.0 was a release candidate intended only for testing; 1.94.1 is stable.
- 1.96.0 and 1.96.1 were release candidates intended only for testing;
  1.96.2 is stable.
- 1.98.0 was a release candidate intended only for testing.

### Withdrawn Linux 1.98.1 build

The Linux 1.98.1 release was withdrawn because of a regression in its
interaction with MagicDNS, pending a fix. Do not use its presence on another
platform as evidence that the Linux build is safe to roll out.

### Funnel repair in 1.102.2

Version 1.102.2 restores incoming Funnel connections that failed in 1.102.1.
Pin at least the repaired build when the deployment depends on Funnel.
