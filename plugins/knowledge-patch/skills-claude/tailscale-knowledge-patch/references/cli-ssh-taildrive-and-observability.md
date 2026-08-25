# CLI, SSH, Taildrive, and Observability

Use this reference for command behavior, machine-readable output, readiness
checks, Tailscale SSH, Taildrive, and local client inspection.

## Configuration and lifecycle commands

### `tailscale configure` stability (since 1.80.0)

`tailscale configure` and its subcommands are no longer alpha except for
`tailscale configure kubeconfig`. The Standalone macOS variant also provides
programmatic system-extension management:

```console
tailscale configure sysext activate
tailscale configure sysext deactivate
tailscale configure sysext status
```

### Disconnect reasons (since 1.84.0)

`tailscale down` accepts `--reason`.

### Duplicate flags (since 1.84.0)

CLI commands reject more than one occurrence of the same flag. Normalize
arguments assembled across scripts, wrappers, and environment variables.

### Interactive confirmation (since 1.88.1)

The CLI requests `y/n` confirmation before significant actions. Audit
unattended calls to affected commands for a supported non-interactive path.

### Readiness and IP assertions (since 1.96.2)

`tailscale wait [flags]` waits for Tailscale resources to become available for
binding. `tailscale ip --assert=<specific-ip-address>` succeeds only when the
address matches one of the node's Tailscale IP addresses.

```console
tailscale wait
tailscale ip --assert=100.64.0.1
```

### Release-candidate track (since 1.96.2)

The `release-candidate` track is accepted by both version inspection and update
commands:

```console
tailscale version --track=release-candidate
tailscale update --track=release-candidate
```

## Inspection commands

### Preferences, identity, and Services (since 1.102.2)

```console
tailscale get
tailscale whoami
tailscale service list
```

These commands expose the current node's preferences, user and device identity,
and visible Tailscale Services. `tailscale status --peers=false` includes the
current device name.

## Tailscale SSH

### Publickey-first clients (since 1.80.0)

As of 1.80.2, Linux, macOS, and FreeBSD again accept clients that skip SSH
`none` authentication and begin with `publickey`, restoring earlier behavior.

### Direct IP without MagicDNS (since 1.88.1)

Tailscale SSH works when the destination is an IP address and MagicDNS is
disabled.

### Linux audit event (since 1.94.1)

Successful Tailscale SSH authentication on Linux emits a `LOGIN` message to the
kernel audit subsystem.

### Account and socket validation (since 1.102.2)

Unix-socket forwarding honors symlink permissions. Tailscale SSH rejects UIDs
and numeric-only usernames, so replace numeric SSH identities with supported
account names.

## Taildrive

### Hosts without `su` (since 1.88.1)

Folder sharing works on Linux and other Unix-like systems without the `su`
command, and shared files remain consistently accessible.

### macOS GUI sharing (since 1.90.1)

The macOS client no longer provides `tailscale drive`. Share directories
through the client GUI.
