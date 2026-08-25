---
name: nftables-knowledge-patch
description: nftables
version: 1.1.6
license: MIT
metadata:
  author: Nevaberry
---


# nftables Knowledge Patch

Use this skill when writing, reviewing, generating, parsing, building, or
operating modern nftables rulesets. Start with the quick references below, then
open only the topic files relevant to the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/expressions-and-protocols.md](references/expressions-and-protocols.md) | Protocol dependencies, bitwise operations, FIB, payloads, overlays, tunnels, and datatypes |
| [references/sets-maps-and-state.md](references/sets-maps-and-state.md) | Sets, maps, intervals, timeouts, conntrack objects, dynamic updates, and resets |
| [references/hooks-nat-and-packet-path.md](references/hooks-nat-and-packet-path.md) | Hooks, policies, NAT, table flags, wildcard devices, and tc ordering |
| [references/cli-files-and-lifecycle.md](references/cli-files-and-lifecycle.md) | Listing, includes, variables, deletion, rule positions, errors, and file safety |
| [references/json-monitoring-and-embedding.md](references/json-monitoring-and-embedding.md) | JSON schema, monitor output, netlink batches, and libnftables embedding |
| [references/build-packaging-and-releases.md](references/build-packaging-and-releases.md) | Dependencies, archives, systemd, Python bindings, checks, and artifact verification |

## Breaking and migration-sensitive behavior

### Emit JSON flag arrays

Treat `flags` as an array even when it contains one item:

```json
{ "flags": ["interval"] }
```

A scalar shape appeared temporarily and was superseded. Parsers consuming
historical output may accept both shapes, but generators should produce arrays.

### Keep XOR right operands constant

The right side of XOR must be a constant. Do not generate computed or variable
XOR operands; the evaluator rejects them.

### Limit binary-operation chains

One expression may contain at most 16 chained binary operations. Split larger
generated calculations into multiple expressions or intermediate values.

### Do not generate DECnet rules

DECnet protocol support was removed. Migrate or reject old DECnet-specific
rules instead of carrying them into a new ruleset.

### Install Python bindings through PEP 517

Use a PEP 517-capable installer. The bindings use a `src` layout and
`pyproject.toml`; the distutils and autotools-driven `setup.py` path is gone.

### Manage libnftables include paths explicitly

Replacing the library include search path no longer causes the default include
directory to be restored. Add every required directory explicitly.

### Opt in to the static-ruleset unit

Upstream installation of the systemd static-ruleset unit is disabled by
default. Configure a unit directory when the build should install it:

```console
./configure --with-unitdir
```

Ancillary systemd files are omitted when the service file is not installed.

## Protocol and expression safety

### Establish dependencies before raw payload access

Raw payload selectors do not establish or validate protocol context. Guard a
raw transport lookup first:

```nft
meta l4proto { tcp, udp } @th,16,16 { 53, 80 }
```

`@ih,offset,length` begins after the layer-4 header. Apply the same dependency
discipline to convenient raw selectors such as `th dport`.

### Let typed named sets establish layer-4 context

A named set declared with `typeof meta l4proto` carries the protocol dependency
into a membership test. A following protocol-dependent statement can use it:

```nft
set protos {
    typeof meta l4proto
    elements = { tcp, udp }
}
meta l4proto @protos tproxy to :1088
```

### Gate compound assignment expressions by kernel

Compound binary assignment right-hand sides require Linux 6.13 or newer:

```nft
ct mark set ct mark & 0xffff0000 | meta mark & 0xffff
```

### Restrict outer traffic before overlay traversal

Geneve and VXLAN inner-header matching requires an explicit outer UDP
restriction. Use the protocol's outer port before inspecting the inner packet:

```nft
netdev filter ingress udp dport 6081 geneve tcp dport 80 counter
netdev filter ingress udp dport 4789 vxlan vlan id 100 counter
```

## High-value set and map patterns

### Bound packet-path updates

Sets updated by rules need finite storage and expiry. Declare `dynamic` and
`timeout`, set both `size` and `timeout`, and choose a garbage-collection
interval that reclaims expired capacity promptly:

```nft
set recent_sources {
    type ipv4_addr
    flags dynamic, timeout
    timeout 5m
    gc-interval 30s
    size 65536
}
```

Do not combine `dynamic` with `interval`. Expired elements occupy capacity
until garbage collection runs.

### Select conntrack objects from maps

Object-reference maps can select conntrack helpers, timeouts, or expectations:

```nft
map helpers {
    type inet_service : ct_helper
    elements = { 21 : "ftp-standard" }
}
ct helper set tcp dport map @helpers
```

### Use typed NAT mappings in `inet` tables

Typed mappings can supply the NAT family and interval values expand to ranges:

```nft
map targets {
    type ipv4_addr : ipv4_addr
    elements = { 192.0.2.10 : 10.0.0.10 }
}
dnat to ip daddr map @targets
```

## Operational workflows

### Prefer idempotent cleanup

`destroy` succeeds when the target is already absent and applies to tables,
chains, rules, sets, maps, elements, flowtables, and named stateful objects:

```nft
destroy table inet stale
destroy element inet filter blocked { 192.0.2.1 }
```

Use `delete` when absence should remain an error.

### Reset state without removing configuration

Use `reset rules` to clear counters and quotas, optionally scoped by family,
table, or chain. Resetting a set or map clears state attached to its elements
without deleting the container.

```nft
reset rules inet filter input
reset set inet filter recent_sources
```

### Treat rule indexes as race-sensitive

Indexes are zero-based and resolved to handles in userspace. Concurrent changes
can shift the effective location. With a location, `add` places a rule after it
and `insert` places a rule before it. Prefer handles when correctness depends on
a stable target.

### Use table flags deliberately

`owner` prevents other processes from changing a table and normally removes it
when the owner exits. Add `persist` to retain the orphaned table for a future
owner. `dormant` unregisters base chains; adding the table again without that
flag reactivates it.

### Monitor richer event streams

Flowtable add/delete events are monitorable. Trace output can include conntrack
direction, state, ID, and status. Monitor consumers must accept quoted device
names in text and the corrected JSON object-delete event type.

## Review checklist

- Confirm raw payload and overlay expressions have explicit protocol guards.
- Confirm generated XOR and long bitwise expressions satisfy evaluator limits.
- Confirm dynamic sets have `size`, `timeout`, suitable flags, and timely GC.
- Confirm JSON consumers tolerate the historical scalar flag shape if needed.
- Confirm NAT maps are typed and do not specify a rejected protocol form.
- Confirm include paths and glob semantics match the caller's working directory.
- Confirm index-based rule edits cannot race with concurrent ruleset changes.
- Confirm build dependencies and systemd installation options match packaging.
- Confirm downloaded archives against their release-specific signature and digest.

