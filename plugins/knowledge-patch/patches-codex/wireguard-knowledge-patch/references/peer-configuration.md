# Peer configuration and synchronization

Use this reference when changing a peer's routes or reconciling live peer
state with a configuration file.

## Incremental `AllowedIPs` updates

Since `1.0.20250521`, `wg set` accepts per-entry update prefixes for
`AllowedIPs` on Linux.

### Add an entry

Prefix a CIDR with `+` to add it if it is not already present:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" allowed-ips +10.20.0.0/16
```

### Remove an entry

Prefix a CIDR with `-` to remove it if it is present:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" allowed-ips -10.10.0.0/16
```

### Combine additions and removals

The same update may carry both forms:

```sh
wg set wg0 peer "$PEER_PUBLIC_KEY" \
  allowed-ips +10.20.0.0/16,-10.10.0.0/16
```

The operation updates only the named entries. Other entries in the peer's
current list remain in place.

### Preserve replacement semantics when intended

A list whose CIDRs have no `+` or `-` prefixes retains the prior behavior: it
replaces the peer's entire `AllowedIPs` list.

Use the forms according to intent:

| Intent | Form |
| --- | --- |
| Add without replacing the list | `+CIDR` |
| Remove without replacing the list | `-CIDR` |
| Define the complete list | Unprefixed CIDR list |

The add and remove forms are conditional: adding an existing entry or
removing an absent entry does not require reconstructing the whole list.

## Clearing a preshared key with `syncconf`

Since `1.0.20260223`, `wg syncconf` reconciles an omitted preshared key with
the live peer state.

When all of the following are true:

- the peer currently has a preshared key;
- the peer remains present in the new configuration; and
- the new peer entry omits `PresharedKey`;

`wg syncconf` explicitly clears the live preshared key.

Apply a stripped `wg-quick` configuration with:

```sh
wg syncconf wg0 <(wg-quick strip wg0)
```

Removing `PresharedKey` from the file therefore takes effect without removing
and recreating the peer.

## Operational decision guide

Use an incremental `AllowedIPs` update when the task names only the CIDRs to
add or remove and the remaining live list must stay intact.

Use an unprefixed `AllowedIPs` list when the supplied value is meant to be the
complete desired list.

When using `syncconf`, distinguish an omitted preshared key from an unchanged
secret: omission now actively removes a live key rather than leaving it
behind.
