# Hooks, NAT, and Packet Path

## Policies and verdicts

An explicitly specified chain policy is always evaluated (since 1.1.5). Do not
rely on the former path that could skip policy evaluation.

Filter chains at the `prerouting` hook may issue `reject` (documented in
1.0.6.1):

```nft
chain early_reject {
    type filter hook prerouting priority filter; policy accept;
    tcp dport 23 reject
}
```

## NAT behavior

The `srcnat` and `dstnat` textual priority aliases are accepted at both `input`
and `output` local hooks (since 1.0.6.1):

```nft
chain local_input {
    type nat hook input priority srcnat; policy accept;
}
chain local_output {
    type nat hook output priority dstnat; policy accept;
}
```

NAT family inference can come from a typed mapping, and interval map values are
expanded to ranges (since 1.0.6.1). This supports address-family-specific maps
inside `inet` tables.

`--optimize` handles `redirect` and `masquerade` in 1.0.6.1. NAT statements
that contain variables are deliberately left unchanged instead of optimized.

The `route_localnet` sysctl is an explicit operational concern as of 1.1.5.
Configurations whose local-routing behavior depends on it should check the host
setting rather than assume a default.

## Table ownership and activation

Table lifecycle flags are documented in 1.1.6-guide:

- `owner` prevents other processes from modifying a table and normally removes
  it when the owner exits.
- `persist` keeps an owner table after its owner exits so another process can
  claim it.
- `dormant` unregisters the table's base chains.

Adding an existing dormant table again without the `dormant` flag reactivates
it:

```nft
add table inet managed { flags owner, persist; }
add table inet maintenance { flags dormant; }
add table inet maintenance
```

## Hook devices

Ingress and egress base chains and flowtables may use a terminal `*` interface
prefix wildcard on supporting kernels (documented in 1.1.6-guide). `list hooks`
reports the resulting attachments:

```nft
add chain inet filter early { type filter hook ingress device "eth*"; priority filter; }
add flowtable inet filter fast { hook ingress priority filter; devices = { "eth*", "wlan0" }; }
```

Devices on an existing `inet` ingress-hook chain can be updated in 1.1.6; the
chain no longer needs to be recreated to change interface membership.

Text listings quote device names in base-chain and flowtable declarations,
including device sets (since 1.1.4):

```nft
devices = { "eth0", "lo" }
```

## Netdev and tc ordering

The packet-path ordering documented in 1.1.6-guide is:

1. Ingress runs network taps, then tc ingress, then netfilter ingress.
2. Egress runs netfilter egress, then tc egress.

A packet redirected at tc ingress never reaches the netfilter layer and skips
netfilter egress. A redirect performed at netfilter ingress remains subject to
netfilter egress.

