# Expressions, Protocols, and Tunnels

## Protocol dependencies

Named sets typed as `meta l4proto` carry a protocol dependency into the rule
(since 1.1.2). A membership match can therefore establish the context required
by a following statement:

```nft
set protos {
    typeof meta l4proto
    elements = { tcp, udp }
}
meta l4proto @protos tproxy to :1088
```

Listings preserve dependency expressions that are necessary for correctness.
They retain `meta nfproto` and keep `meta l4proto` before raw transport-header
expressions such as `@th,0,16` (since 1.1.2).

Raw payload access does not establish dependencies (documented in 1.1.6-guide).
`@ih,offset,length` starts after the layer-4 header, and selectors such as
`th dport` do not validate the protocol. Exclude incompatible protocols first:

```nft
meta l4proto { tcp, udp } @th,16,16 { 53, 80 }
```

## Bitwise and relational expressions

Assignment right-hand sides may combine binary operators and variable operands
(since 1.1.2), provided the host uses Linux 6.13 or newer:

```nft
ct mark set ct mark & 0xffff0000 | meta mark & 0xffff
meta mark set meta mark & 0xffff0000 | meta cpu << 8 | iif
```

Bitfield payload statements also accept binary updates, for example:

```nft
ip dscp set ip dscp | 0x1
```

The optimizer can merge rules that share a bitmask expression into a set-valued
comparison (since 1.1.2):

```nft
tcp flags & (fin | syn | rst | ack | urg) == { fin, syn, ack }
```

Ranges use one native `range eq` netlink expression with start and end values,
instead of separate `gte` and `lte` comparisons (since 1.1.2).

The XOR right operand must be constant (since 1.1.5); computed or variable
right operands are rejected. An expression may chain no more than 16 binary
operations (since 1.0.6.1), so ruleset generators must split larger chains.

## FIB and time expressions

`fib ... check` yields `exists` or `missing` (since 1.1.4). It works as a direct
match, a verdict-map key, or part of a map expression used by a statement:

```nft
fib daddr . iif check missing
fib daddr check vmap { missing : drop, exists : accept }
meta mark set fib daddr check . ct mark map { exists . 0x00000000 : 0x0000000a, missing . 0x00000001 : 0x0000000b }
```

Overnight `meta hour` ranges work across midnight again in 1.1.4, correcting
the behavior in 1.1.3:

```nft
meta hour "21:00"-"02:00"
```

## Datatypes and symbolic protocol values

MPTCP subtype matching accepts `mp-capable`, `mp-join`, `dss`, `add-addr`,
`remove-addr`, `mp-prio`, `mp-fail`, `mp-fastclose`, and `mp-tcprst` as symbolic
values (since 1.1.2).

`fib oifname` uses the `ifname` datatype, and IPv4 option address fields use the
IPv4-address datatype (since 1.1.2). Conntrack `proto-src` and `proto-dst` use
`inet_service` (since 1.0.6.1), enabling service names and service-typed maps:

```nft
ct original proto-dst ssh accept
```

The text parser rejects non-serializable `typeof` expressions. Stateful
statements are valid only in set or map definitions, and NAT maps that specify
a protocol are rejected (since 1.1.2).

## Encapsulation and tunnel metadata

Overlay traversal is documented in 1.1.6-guide. `gre` can inspect its own
fields and an inner IPv4 or IPv6 packet. `geneve`, `gretap`, and `vxlan` can
traverse encapsulated Ethernet, VLAN, IPv4, IPv6, TCP, and UDP headers. Geneve
and VXLAN must first restrict the outer UDP traffic:

```nft
netdev filter ingress gre ip daddr 9.9.9.9 counter
netdev filter ingress udp dport 6081 geneve tcp dport 80 counter
netdev filter ingress udp dport 4789 vxlan vlan id 100 counter
```

Tunnel templates, objects, statements, and expressions cover VXLAN, ERSPAN,
and Geneve in 1.1.6. Tunnel objects can be listed and deleted, and JSON can
represent their statements. The source is optional; when present, source and
destination values must be symbolic expressions. Duplicate tunnel or IP
endpoint sections are rejected.

`meta ibrhwaddr` exposes ingress-bridge hardware-address metadata in 1.1.6.
DECnet support was removed in 1.0.6.1; protocol-specific DECnet rules require
migration rather than direct reuse.

