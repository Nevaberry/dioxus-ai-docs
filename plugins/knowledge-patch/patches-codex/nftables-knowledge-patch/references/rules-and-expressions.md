# Rules and expressions

Use this reference when authoring matches, assignments, payload expressions, or
ruleset generators.

## Protocol dependencies and payload access (1.1.2, 1.1.6-guide)

A named set typed as `meta l4proto` carries its protocol dependency into the
rule. A membership test can therefore establish the context required by a later
statement:

```nft
set protos {
    typeof meta l4proto
    elements = { tcp, udp }
}
meta l4proto @protos tproxy to :1088
```

Listings preserve required `meta nfproto` expressions and keep
`meta l4proto` ahead of raw transport-header expressions such as `@th,0,16`.
Do not remove these apparent redundancies from generated rules.

Raw payload selectors do not create or validate dependencies. `@ih,offset,length`
addresses bits after the layer-4 header, while raw transport selectors such as
`th dport` can reinterpret unrelated protocols. Exclude unsuitable protocols
first:

```nft
meta l4proto { tcp, udp } @th,16,16 { 53, 80 }
```

## Binary and bitfield expressions (1.1.2, 1.1.5, 1.0.6.1)

Assignment right-hand sides can combine binary operations and variable
operands. This requires Linux 6.13 or newer:

```nft
ct mark set ct mark & 0xffff0000 | meta mark & 0xffff
meta mark set meta mark & 0xffff0000 | meta cpu << 8 | iif
```

Bitfield payload statements can also apply binary updates:

```nft
ip dscp set ip dscp | 0x1
```

The XOR right operand must be a constant. An expression can chain at most 16
binary operations; generators must split a larger computation.

With `-o` or `--optimize`, rules sharing a bitmask expression can be merged into
a set-valued comparison:

```nft
tcp flags & (fin | syn | rst | ack | urg) == { fin, syn, ack }
```

## Native ranges and concatenations (1.1.2, 1.1.5)

Netlink represents a range as one `range eq` expression with start and end
values rather than separate `gte` and `lte` comparisons. Do not require the old
pair when parsing netlink expressions.

Range aggregation in concatenated sets retains the correct datatype. Ruleset
generators can combine concatenated ranges without compensating for the earlier
type-evaluation failure.

## FIB and route checks (1.1.4)

`fib ... check` produces `exists` or `missing`. Match it directly, dispatch
through a verdict map, or include it in a map expression used by a statement:

```nft
fib daddr . iif check missing
fib daddr check vmap { missing : drop, exists : accept }
meta mark set fib daddr check . ct mark map {
    exists . 0x00000000 : 0x0000000a,
    missing . 0x00000001 : 0x0000000b
}
```

Relational FIB expressions can be serialized to JSON.

## Time, services, and field datatypes (1.1.2, 1.1.4, 1.0.6.1)

An overnight `meta hour` interval can cross midnight:

```nft
meta hour "21:00"-"02:00"
```

`fib oifname` has the `ifname` datatype. IPv4 option address fields have the
IPv4-address datatype. `ct proto-src` and `ct proto-dst` use `inet_service`, so
service names and service-typed maps work:

```nft
ct original proto-dst ssh accept
```

Conntrack timeout-policy values accept time specifications:

```nft
ct timeout web-timeout {
    protocol tcp
    l3proto ip
    policy = { established : 2h, close : 10s }
}
```

## MPTCP and bridge metadata (1.1.2, 1.1.6)

`tcp option mptcp subtype` supports these symbolic values:

- `mp-capable`
- `mp-join`
- `dss`
- `add-addr`
- `remove-addr`
- `mp-prio`
- `mp-fail`
- `mp-fastclose`
- `mp-tcprst`

The expression can type a set:

```nft
set mptcp_types {
    typeof tcp option mptcp subtype
    elements = { mp-join, dss }
}
```

`meta ibrhwaddr` exposes the ingress-bridge hardware address for matching.

## Policies, validation, and limits (1.1.2, 1.1.5, 1.0.6.1)

An explicitly specified chain policy is always evaluated. Do not depend on an
older path that skipped policy evaluation.

The parser and evaluator enforce these boundaries:

- text `typeof` expressions must be serializable;
- stateful statements belong only in set or map definitions;
- a NAT map that specifies a protocol is rejected;
- byte-mode limits accept `burst 0 bytes`;
- listings print the default byte-rate burst even when input omitted it.

```nft
limit rate 1 mbytes/second burst 0 bytes accept
```
