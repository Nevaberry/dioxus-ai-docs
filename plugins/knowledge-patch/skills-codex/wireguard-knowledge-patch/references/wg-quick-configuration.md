# `wg-quick` configuration and lifecycle

Use this reference for configuration discovery, secret-loading hooks, hook
parsing, DNS setup, and Linux interface creation.

## Configuration discovery from an interface name

In the `1.0.20260223-guide` behavior, a name-only invocation such as:

```sh
wg-quick up wg0
```

first searches:

```text
/etc/wireguard/INTERFACE.conf
```

For `wg0`, that first candidate is `/etc/wireguard/wg0.conf`. If the
configuration is not found there, lookup continues through distro-specific
search paths.

The search is ordered, so the `/etc/wireguard` candidate takes precedence.
Do not treat that directory as the only possible location for a name-only
invocation.

## Merging configuration after `PreUp`

Since `1.0.20260223`, `wg-quick` uses `wg addconf` rather than `wg setconf`
when applying configuration to a newly created interface.

This matters when `PreUp` installs a WireGuard setting that is intentionally
omitted from the file. The later configuration step merges the file's
settings and leaves the hook-installed setting intact.

For example, load a private key from a secret store:

```ini
[Interface]
Address = 10.0.0.1/24
PreUp = wg set %i private-key <(pass WireGuard/private-keys/%i)
```

The private key set by `PreUp` survives because the stripped configuration
does not replace the entire interface state.

## Shell-aware lifecycle hooks

Since `1.0.20260223`, values of all four lifecycle hooks are passed to the
shell without first being cut off at `#`:

- `PreUp`
- `PostUp`
- `PreDown`
- `PostDown`

Shell syntax now decides what the hash character means.

```ini
PostUp = printf '%s\n' 'wg#ready' # shell comment
```

Here, the quoted hash is part of the string and the later unquoted hash starts
a shell comment. Escaped hash characters likewise remain part of the command.

When reviewing an existing hook, apply shell quoting rules to the complete
value; do not assume that `wg-quick` truncates it independently.

## Resolvconf prefix selection

Since `1.0.20260223`, Linux `wg-quick` uses the legacy `tun.` interface-prefix
workaround from:

```text
/etc/resolvconf/interface-order
```

only when the `resolvconf` executable is not a symlink.

This distinguishes a legacy resolvconf installation from a system that has
migrated to a systemd resolver wrapper but still has a stale
`interface-order` file. In the migrated case, the stale file no longer forces
a bogus `tun.` prefix that makes `DNS=` setup fail.

When diagnosing this path, consider both:

1. whether `/etc/resolvconf/interface-order` contains the workaround; and
2. whether the active `resolvconf` executable is a symlink.

## Keyword-like interface names on Linux

Since `1.0.20250521`, Linux `wg-quick` supplies `dev` explicitly when it
creates a link. This prevents an interface name that overlaps an `ip-link`
keyword from being parsed as part of the command syntax.

For example:

```sh
wg-quick up type
```

The name `type` is treated as the interface name. A keyword-like name does not
by itself require a workaround or rename.
