# CLI and peer state

## Incremental `AllowedIPs` updates

Batch `1.0.20250521` adds incremental `AllowedIPs` operations to `wg set` on
Linux. Prefix a CIDR with `+` to add it if it is absent, or with `-` to remove
it if it is present:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" \
  allowed-ips +10.20.0.0/16,-10.10.0.0/16
```

The operation can contain additions and removals together. Because each
operation is conditional on current membership, callers do not need to rebuild
the peer's complete route list for a small change.

An unprefixed list retains the earlier replacement behavior:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" \
  allowed-ips 10.20.0.0/16,10.30.0.0/16
```

Select the syntax from the desired state transition:

| Desired transition | Syntax |
| --- | --- |
| Add a CIDR without replacing other entries | `+CIDR` |
| Remove a CIDR without replacing other entries | `-CIDR` |
| Replace the peer's entire list | Unprefixed CIDR list |

The prefixes belong to individual CIDRs. In automation, do not accidentally
mix an unprefixed replacement list into a command intended to make only
incremental changes.

## Clearing an omitted preshared key

Batch `1.0.20260223` changes how `wg syncconf` handles a peer whose live state
contains a preshared key but whose new configuration omits `PresharedKey`.
Synchronization now explicitly clears the live preshared key.

```sh
wg syncconf wg0 <(wg-quick strip wg0)
```

The intended transition is:

```text
live peer has preshared key
             +
new peer configuration omits PresharedKey
             |
             v
live peer has no preshared key
```

Removing the setting from the source configuration is sufficient; removing
and recreating the peer is unnecessary.

### Safe review workflow

1. Compare the peer entry in the live state with the configuration being
   passed to `syncconf`.
2. If `PresharedKey` was removed from the new configuration, expect the live
   key to be cleared.
3. Treat the omission as a security-relevant state change during review.
4. Run the normal synchronization command.
5. Inspect the resulting live configuration when confirmation is required.

Do not carry forward the assumption that omission preserves a previous live
preshared key. That assumption gives the wrong result for this synchronization
behavior.
