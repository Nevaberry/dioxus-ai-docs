# `wg-quick` configuration and Linux networking

## Interface creation with keyword-like names

In batch `1.0.20250521`, Linux `wg-quick` supplies `dev` explicitly when
creating a link. An interface name that overlaps an `ip-link` keyword is no
longer parsed as that keyword.

```sh
wg-quick up type
```

This removes the parsing ambiguity at link creation. A workaround that renamed
an otherwise valid interface solely because the old command shape confused it
with a keyword is no longer required.

## Configuration search by interface name

Batch `1.0.20260223-guide` documents the lookup performed when `wg-quick`
receives an interface name instead of a configuration path.

For:

```sh
wg-quick up wg0
```

the first candidate is:

```text
/etc/wireguard/wg0.conf
```

If that file is absent, `wg-quick` continues through distro-specific search
paths. Troubleshoot lookup in that order:

1. Check the matching file below `/etc/wireguard`.
2. If it is absent, check the distribution's additional search locations.
3. Account for which same-named configuration appears first in the search.

## Merging file configuration after `PreUp`

In batch `1.0.20260223`, a newly created interface is configured with
`wg addconf` rather than `wg setconf`. The file is merged with settings already
installed by `PreUp`.

For example, a private key can be loaded from a secret store:

```ini
[Interface]
Address = 10.0.0.1/24
PreUp = wg set %i private-key <(pass WireGuard/private-keys/%i)
```

Because the file omits the private key, the value installed by `PreUp` survives
the later configuration load.

The important boundary is omission: this behavior preserves a setting that
the hook installs and the file does not contain. It should not be interpreted
as a general rule that a file-supplied value cannot affect existing state.

## Shell-aware lifecycle-hook comments

Also in batch `1.0.20260223`, values of `PreUp`, `PostUp`, `PreDown`, and
`PostDown` are passed to the shell without first being truncated at `#`.

```ini
PostUp = printf '%s\n' 'wg#ready' # shell comment
```

Shell parsing now makes the distinction:

- The `#` inside `'wg#ready'` is quoted and remains part of the argument.
- The later unquoted `# shell comment` begins an actual shell comment.
- An escaped hash character likewise remains command data.

When reviewing hook commands, interpret quoting and escaping across the whole
value. Do not cut off the raw configuration string at its first hash.

## Resolver-prefix behavior after migration

In batch `1.0.20260223`, Linux `wg-quick` applies the legacy `tun.` interface
prefix workaround from `/etc/resolvconf/interface-order` only when the
`resolvconf` executable is not a symlink.

This avoids using a stale prefix rule when a system has migrated to a systemd
resolver wrapper but retained the old interface-order file. Without the
symlink check, `DNS=` setup could fail because the stale file supplied a bogus
prefix.

When diagnosing this case, inspect both inputs:

| Check | Why it matters |
| --- | --- |
| `/etc/resolvconf/interface-order` | It may still contain the legacy `tun.` rule |
| Whether `resolvconf` is a symlink | A symlink suppresses that legacy workaround |

Do not infer active legacy behavior from the presence of the interface-order
file alone.

## Conditional `src_valid_mark` writes

During Linux IPv4 default-route setup, batch `1.0.20260223` makes `wg-quick`
write:

```text
net.ipv4.conf.all.src_valid_mark=1
```

only if its current value is not already `1`.

This splits restricted-namespace behavior into two cases:

| Current value | Required action |
| --- | --- |
| Already `1` | No write is attempted, so setup does not need sysctl write permission for this step |
| Any other value | `wg-quick` must write `1`, so the namespace still needs permission |

A host can therefore preconfigure the required value for a namespace that
forbids sysctl writes. When setup still fails, check the observed value before
concluding that the conditional behavior should have avoided the write.
