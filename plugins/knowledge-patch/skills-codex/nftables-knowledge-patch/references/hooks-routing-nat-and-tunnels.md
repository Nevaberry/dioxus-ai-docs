# Hooks, routing, NAT, and tunnels

Use this reference when placing chains, attaching devices, translating
addresses, rejecting traffic early, or inspecting encapsulated packets.

## NAT hook priorities and typed mappings (1.0.6.1)

The textual `srcnat` and `dstnat` priorities are accepted on both `input` and
`output` base chains:

```nft
chain local_input {
    type nat hook input priority srcnat; policy accept;
}
chain local_output {
    type nat hook output priority dstnat; policy accept;
}
```

The evaluator can infer the NAT family from a typed mapping and expands an
interval-valued mapping to a range. This is useful in `inet` tables:

```nft
map targets {
    type ipv4_addr : ipv4_addr
    elements = { 192.0.2.10 : 10.0.0.10 }
}
dnat to ip daddr map @targets
```

NAT maps that specify a protocol are rejected.

## Prerouting reject and local routing (1.0.6.1, 1.1.5)

A filter chain at the `prerouting` hook may issue a reject verdict:

```nft
chain early_reject {
    type filter hook prerouting priority filter; policy accept;
    tcp dport 23 reject
}
```

Configurations affected by local-route behavior must verify the host's
`route_localnet` sysctl explicitly.

## NAT optimization (1.0.6.1)

`--optimize` recognizes `redirect` and `masquerade`. NAT statements containing
variables are skipped deliberately rather than rewritten.

## Overlay header traversal (1.1.6-guide)

`gre` can inspect its own fields and an inner IPv4 or IPv6 packet. `geneve`,
`gretap`, and `vxlan` can traverse encapsulated Ethernet, VLAN, IPv4, IPv6, TCP,
and UDP headers.

Geneve and VXLAN rules must constrain the outer UDP traffic before accessing
inner headers:

```nft
netdev filter ingress gre ip daddr 9.9.9.9 counter
netdev filter ingress udp dport 6081 geneve tcp dport 80 counter
netdev filter ingress udp dport 4789 vxlan vlan id 100 counter
```

`@ih,offset,length` addresses bits after the layer-4 header. Raw payload
expressions do not establish protocol dependencies; add explicit guards.

## Tunnel objects (1.1.6)

Tunnel templates, objects, statements, and expressions cover VXLAN, ERSPAN, and
Geneve. Tunnel objects can be listed and deleted, and JSON can represent the
objects with their statements.

A tunnel source may be omitted. When present, source and destination values
must be symbolic expressions. Duplicate tunnel sections or duplicate IP
endpoint sections are rejected.

## Hook device wildcards (1.1.6-guide)

On supporting kernels, ingress and egress base chains and flowtables can use an
interface name with a trailing `*` to follow every interface with that prefix:

```nft
add chain inet filter early {
    type filter hook ingress device "eth*"; priority filter;
}
add flowtable inet filter fast {
    hook ingress priority filter;
    devices = { "eth*", "wlan0" };
}
```

Use `list hooks` to inspect the resulting attachments.

## Updating ingress devices (1.1.6)

Device membership on an existing `inet` ingress-hook chain can be updated. A
device change no longer requires recreating the chain.

Text listings and monitor output quote hook device names, including device sets:

```nft
devices = { "eth0", "lo" }
```

## Netdev and tc ordering (1.1.6-guide)

Ingress processing order is:

1. network taps;
2. tc ingress;
3. netfilter ingress.

Egress processing order is:

1. netfilter egress;
2. tc egress.

A packet redirected at tc ingress never reaches netfilter ingress and therefore
skips netfilter egress. A redirect performed at netfilter ingress remains
subject to netfilter egress.
