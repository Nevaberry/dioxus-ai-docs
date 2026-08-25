---
name: wireguard-knowledge-patch
description: WireGuard
version: 1.0.20260223
license: MIT
metadata:
  author: Nevaberry
---



# WireGuard

Use this skill when configuring or operating WireGuard with `wg`, `wg-quick`,
or `wg-quick@.service`, especially when changing peers in place, loading
secrets from hooks, managing DNS, or ordering dependent systemd units.

Start with the compatibility-sensitive behavior below. Then open the reference
that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [peer-configuration.md](references/peer-configuration.md) | Incremental `AllowedIPs` changes and preshared-key removal with `syncconf` |
| [wg-quick-configuration.md](references/wg-quick-configuration.md) | Configuration discovery, `PreUp` merging, hook comments, DNS handling, and interface names |
| [linux-startup-and-routing.md](references/linux-startup-and-routing.md) | systemd target ordering and conditional `src_valid_mark` writes |

## Compatibility- and security-sensitive behavior

### Preserve settings installed by `PreUp`

When `wg-quick` configures a newly created interface, it merges the stripped
WireGuard configuration with `wg addconf`. A setting installed by `PreUp` and
omitted from the file therefore remains installed.

This supports loading a private key from a secret store without placing the
key in the configuration:

```ini
[Interface]
Address = 10.0.0.1/24
PreUp = wg set %i private-key <(pass WireGuard/private-keys/%i)
```

Do not reason about this flow as though the later configuration load replaces
the complete interface state with `wg setconf`.

### Expect `syncconf` to clear an omitted preshared key

If a peer has a live preshared key but the new configuration omits
`PresharedKey`, `wg syncconf` explicitly clears that live key. Removing the
setting from the file is sufficient; the peer does not need to be removed and
recreated.

```sh
wg syncconf wg0 <(wg-quick strip wg0)
```

Treat this as a security-sensitive transition. An omitted `PresharedKey` in
the new configuration means that the synchronized peer should no longer use
the previous preshared key.

### Let the shell interpret hook comments

`PreUp`, `PostUp`, `PreDown`, and `PostDown` values reach the shell without
being truncated at the first `#`.

```ini
PostUp = printf '%s\n' 'wg#ready' # shell comment
```

Quoted or escaped hash characters remain part of the command. An actual
unquoted shell comment still behaves as a comment.

Review hooks that relied on unconditional truncation at `#`; their effective
command may now be longer than expected.

### Do not force the legacy resolvconf prefix after migration

On Linux, `wg-quick` applies the legacy `tun.` prefix workaround from
`/etc/resolvconf/interface-order` only when the `resolvconf` executable is not
a symlink.

When a system has migrated to a systemd resolver wrapper, a stale
`interface-order` file no longer causes `DNS=` setup to use a bogus prefix.
Diagnose the executable type as well as the legacy file when investigating DNS
setup behavior.

## High-use peer updates

### Add and remove individual `AllowedIPs`

Use a `+` prefix to add a CIDR only when it is absent, and a `-` prefix to
remove a CIDR only when it is present:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" \
  allowed-ips +10.20.0.0/16,-10.10.0.0/16
```

This changes individual entries without replacing the peer's entire
`AllowedIPs` list.

The prefixes control the update mode:

| Form | Effect |
| --- | --- |
| `+CIDR` | Add the CIDR if absent |
| `-CIDR` | Remove the CIDR if present |
| Unprefixed list | Replace the previous list |

Choose deliberately between incremental and replacement forms. An
unprefixed list retains the complete-list replacement behavior.

## `wg-quick` invocation and discovery

### Allow configuration lookup to continue

When `wg-quick` receives only an interface name, it checks:

```text
/etc/wireguard/INTERFACE.conf
```

first, then continues through distro-specific search paths.

```sh
wg-quick up wg0
```

Do not conclude that a name-only invocation has no configuration merely
because the file is absent from `/etc/wireguard`; account for the later
distro-specific lookup.

### Interface names may overlap `ip-link` keywords

On Linux, `wg-quick` passes `dev` explicitly while creating the link.
Interface names that overlap an `ip-link` keyword are therefore not
misparsed as link syntax.

```sh
wg-quick up type
```

Avoid adding a rename workaround solely because a valid interface name looks
like an `ip-link` keyword.

## Linux startup and routing

### Order consumers after every enabled instance

The systemd template installs into `wg-quick.target` and declares itself
before that target. The target is not considered started until its enabled
`wg-quick@.service` instances have been started.

A unit that needs all enabled instances can use:

```ini
[Unit]
Wants=wg-quick.target
After=wg-quick.target
```

Use the target for aggregate ordering instead of guessing individual instance
names in the dependent unit.

### Preconfigure `src_valid_mark` in restricted namespaces

During Linux IPv4 default-route setup, `wg-quick` writes:

```text
net.ipv4.conf.all.src_valid_mark=1
```

only when the current value is not already `1`.

If the host has already set the value, setup can succeed in a restricted
namespace that forbids sysctl writes. If the value is not `1`, the namespace
still needs permission to change it.

## Task checklist

### Updating a peer in place

1. Decide whether the new `AllowedIPs` value is a delta or a complete
   replacement.
2. Use `+` and `-` prefixes only for the delta form.
3. If synchronizing a file, remember that omitting `PresharedKey` clears a
   live preshared key.
4. Open [peer-configuration.md](references/peer-configuration.md) for the
   detailed semantics.

### Bringing up an interface

1. For a name-only invocation, allow both `/etc/wireguard` and
   distro-specific discovery.
2. Keep secret-loaded settings out of the file when `PreUp` installs them;
   the subsequent merge preserves them.
3. Let shell quoting determine whether `#` is data or a comment in lifecycle
   hooks.
4. On Linux, account for symlink-sensitive resolvconf handling and explicit
   `dev` link creation.

### Preparing system services or containers

1. Depend on `wg-quick.target` when a unit requires all enabled instances.
2. In a restricted namespace, check whether the host has already set
   `src_valid_mark` to `1`.
3. If it has not, provide permission for the required sysctl write.
4. Open
   [linux-startup-and-routing.md](references/linux-startup-and-routing.md)
   for the exact ordering and routing conditions.
