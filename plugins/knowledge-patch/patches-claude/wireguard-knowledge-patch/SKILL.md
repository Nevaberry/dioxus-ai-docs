---
name: wireguard-knowledge-patch
description: WireGuard
version: "1.0.20260223"
license: MIT
metadata:
  author: Nevaberry
---



# WireGuard Knowledge Patch

Use this skill when changing WireGuard peer state, writing or debugging
`wg-quick` configuration, synchronizing a live interface, or coordinating
WireGuard interfaces with systemd.

## Reference index

| Reference | Topics |
| --- | --- |
| [cli-and-peer-state.md](references/cli-and-peer-state.md) | Incremental `AllowedIPs` changes and preshared-key removal with `syncconf` |
| [wg-quick-configuration.md](references/wg-quick-configuration.md) | Interface creation, configuration lookup, `PreUp` state, hook comments, DNS, and policy-routing sysctls |
| [systemd-integration.md](references/systemd-integration.md) | Waiting for all enabled `wg-quick` instances with `wg-quick.target` |

## Compatibility-sensitive behavior

### Preserve state installed by `PreUp`

When a newly created interface is configured, `wg-quick` merges the file with
state already installed by `PreUp`. Settings that the hook installs and the
file omits survive the configuration load.

This supports loading a private key from a secret store without also placing
the key in the configuration file:

```ini
[Interface]
Address = 10.0.0.1/24
PreUp = wg set %i private-key <(pass WireGuard/private-keys/%i)
```

Keep the runtime-only setting out of the file. If the file supplies the same
setting, it participates in the merge and can replace the hook-installed
value.

For the exact merge behavior and related hook parsing, read
[wg-quick-configuration.md](references/wg-quick-configuration.md).

### Remove a preshared key with `syncconf`

If a live peer has a preshared key and the replacement configuration omits
`PresharedKey`, `wg syncconf` clears the live key. There is no need to delete
and recreate the peer merely to remove that key.

```sh
wg syncconf wg0 <(wg-quick strip wg0)
```

Treat omission as an intentional removal when reviewing a configuration diff.
Do not assume that an omitted key leaves the previous runtime value intact.

See [cli-and-peer-state.md](references/cli-and-peer-state.md) for the state
transition and a verification-oriented workflow.

### Let the shell interpret hook comments

`PreUp`, `PostUp`, `PreDown`, and `PostDown` values reach the shell without
being cut off at the first `#`. Quoted and escaped hash characters remain
command data; an unquoted shell comment remains a comment.

```ini
PostUp = printf '%s\n' 'wg#ready' # shell comment
```

When migrating a workaround that assumed unconditional truncation, evaluate
the complete value under shell quoting and comment rules.

## High-value operational changes

### Edit `AllowedIPs` incrementally

On Linux, `wg set` accepts a `+` prefix to add one CIDR if absent and a `-`
prefix to remove one CIDR if present. This avoids reconstructing and replacing
the peer's complete `AllowedIPs` list for a small route change.

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" \
  allowed-ips +10.20.0.0/16,-10.10.0.0/16
```

A list whose CIDRs have no prefixes keeps replacement behavior. Choose the
form deliberately:

| Intent | Form |
| --- | --- |
| Add selected routes | Prefix each added CIDR with `+` |
| Remove selected routes | Prefix each removed CIDR with `-` |
| Replace the complete list | Supply an unprefixed list |

Mixed additions and removals can be submitted in one comma-separated value.
Read [cli-and-peer-state.md](references/cli-and-peer-state.md) before building
route-management automation.

### Use interface names that resemble `ip-link` keywords

On Linux, `wg-quick` passes `dev` explicitly while creating the link.
An interface name that also looks like an `ip-link` keyword is therefore not
misparsed as that keyword.

```sh
wg-quick up type
```

Do not keep name-avoidance workarounds solely for the earlier ambiguous link
creation syntax.

### Resolve a configuration from an interface name

When `wg-quick` receives only an interface name, it first checks:

```text
/etc/wireguard/INTERFACE.conf
```

If the file is not there, lookup continues through distro-specific search
paths.

```sh
wg-quick up wg0
```

For deterministic troubleshooting, check `/etc/wireguard/wg0.conf` first,
then account for the distribution's additional locations. Full guidance is in
[wg-quick-configuration.md](references/wg-quick-configuration.md).

### Diagnose `DNS=` after a resolver migration

On Linux, the legacy `tun.` prefix workaround from
`/etc/resolvconf/interface-order` is applied only when the `resolvconf`
executable is not a symlink.

This prevents a stale interface-order file from injecting a bogus prefix after
migration to a systemd resolver wrapper. If `DNS=` setup fails around interface
naming, inspect both the interface-order file and whether the executable is a
symlink before assuming the old prefix rule applies.

### Avoid unnecessary `src_valid_mark` writes

During Linux IPv4 default-route setup, `wg-quick` writes:

```text
net.ipv4.conf.all.src_valid_mark=1
```

only when the current value is not already `1`.

This matters in restricted namespaces: setup can proceed without sysctl write
permission when the host has already set the value to `1`. If the current
value differs, the namespace still needs permission to change it.

Do not diagnose every denied sysctl write the same way. First determine whether
the required value was already in effect.

## systemd ordering

Enabled `wg-quick@.service` instances install into `wg-quick.target` and order
themselves before that target. A dependent unit can therefore wait until all
enabled instances pulled in by the target have started:

```ini
[Unit]
Wants=wg-quick.target
After=wg-quick.target
```

Use both relationships for a unit that should pull in the aggregate target and
start after it. See [systemd-integration.md](references/systemd-integration.md)
for the ordering model and its boundary.

## Review checklist

- Decide whether an `AllowedIPs` operation is incremental or a full
  replacement.
- Treat a missing `PresharedKey` in a synchronized configuration as removal.
- Preserve runtime-only state installed by `PreUp` by omitting that setting
  from the file.
- Read hook values using shell quoting, escaping, and comment semantics.
- Check the primary `/etc/wireguard` path before distro-specific locations.
- When investigating `DNS=`, distinguish a real `resolvconf` executable from a
  symlinked resolver wrapper.
- Check the current `src_valid_mark` value before requiring namespace write
  permission.
- Order dependent systemd units after `wg-quick.target`, not merely after one
  instance, when they require all enabled instances.

## Loading references

Load only the topic needed for the task:

- For peer-route mutations or live peer synchronization, load
  [cli-and-peer-state.md](references/cli-and-peer-state.md).
- For `wg-quick` files, hooks, interface startup, resolver behavior, or Linux
  policy routing, load
  [wg-quick-configuration.md](references/wg-quick-configuration.md).
- For aggregate service readiness and dependent units, load
  [systemd-integration.md](references/systemd-integration.md).
