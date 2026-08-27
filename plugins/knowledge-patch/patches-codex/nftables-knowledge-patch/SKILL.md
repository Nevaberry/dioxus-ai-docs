---
name: nftables-knowledge-patch
description: nftables
version: "1.1.6"
license: MIT
metadata:
  author: Nevaberry
---


# nftables Knowledge Patch

Use this skill when writing, reviewing, generating, loading, or troubleshooting
nftables rulesets, JSON commands, libnftables integrations, monitoring tools, or
source builds.

## How to apply this skill

1. Identify the nftables userspace version, kernel version, and table families
   involved.
2. Read the breaking and compatibility checks below before changing syntax or
   serialized output.
3. Open the topic reference that matches the task.
4. Validate generated rules with the real parser and, where safe, the target
   kernel; some expression support depends on both userspace and kernel.
5. Treat normalized text and JSON listings as interfaces that can change shape.
6. Preserve explicit protocol dependencies before raw or encapsulated payload
   access.

## Reference index

| Reference | Topics |
| --- | --- |
| [Rules and expressions](references/rules-and-expressions.md) | Protocol dependencies, bitwise expressions, FIB checks, datatypes, time matches, policies, limits |
| [Sets, maps, and state](references/sets-maps-and-state.md) | `typeof`, intervals, object maps, timeouts, dynamic updates, replication, reset |
| [Hooks, routing, NAT, and tunnels](references/hooks-routing-nat-and-tunnels.md) | Hook devices, tc ordering, NAT, prerouting reject, overlays, tunnel objects |
| [JSON, monitoring, and automation](references/json-monitoring-and-automation.md) | JSON shapes and coverage, monitor events, trace data, includes, variables, file targets |
| [Operations, builds, and releases](references/operations-build-and-releases.md) | Idempotent lifecycle, listings, errors, dependencies, packaging, bindings, artifact verification |

## Breaking and compatibility-critical changes

### Expect JSON arrays for flags

Current JSON output preserves one-item arrays:

```json
{ "flags": ["interval"] }
```

One intervening release emitted a single flag as a scalar. Consumers that read
saved or live output across releases should accept both forms, but generators
should emit the array form. See
[JSON, monitoring, and automation](references/json-monitoring-and-automation.md).

### Keep XOR and long binary expressions within evaluator limits

The right operand of XOR must be a constant. Any one expression may chain at
most 16 binary operations. Split generated computations that exceed the limit.
Compound assignment expressions are supported, but require a sufficiently new
kernel:

```nft
ct mark set ct mark & 0xffff0000 | meta mark & 0xffff
```

Read [Rules and expressions](references/rules-and-expressions.md) before
emitting computed assignments.

### Preserve raw-payload protocol guards

Raw payload selectors do not create or validate protocol dependencies. Establish
the context first:

```nft
meta l4proto { tcp, udp } @th,16,16 { 53, 80 }
```

Named `meta l4proto` sets can satisfy that dependency. For Geneve and VXLAN,
also constrain the outer UDP traffic before inspecting inner fields.

### Rebuild assumptions about include paths

Libnftables does not restore its default include directory after an embedder
replaces the include search path. Add every required directory explicitly.
Ruleset include globs may legitimately match nothing, ignore dotfiles, and load
matches in deterministic C-locale order.

### Treat systemd installation as opt-in

The upstream static-ruleset unit is installed only when its unit directory is
enabled. Ancillary systemd files are not installed when the service file is
omitted:

```console
./configure --with-unitdir
```

Packaging automation must request the unit deliberately.

### Remove DECnet-specific rules

DECnet support is gone. Protocol-specific DECnet constructs have no direct
forward-compatible path and must be redesigned rather than copied unchanged.

## High-value rule features

### Test route existence with FIB

`fib ... check` yields `exists` or `missing` and works in a direct match, verdict
map, or statement map:

```nft
fib daddr . iif check missing
fib daddr check vmap { missing : drop, exists : accept }
```

Overnight `meta hour` ranges may cross midnight, and `fib oifname` carries the
interface-name datatype.

### Use symbolic MPTCP subtypes

`tcp option mptcp subtype` accepts symbolic subtype names such as `mp-capable`,
`mp-join`, `dss`, `add-addr`, and `mp-fastclose`. It can also type a named set.

### Update bitfields directly

Bitfield payload statements accept binary updates:

```nft
ip dscp set ip dscp | 0x1
```

The optimizer can merge rules that share a bitmask expression into a set-valued
comparison. It also understands `redirect` and `masquerade`, while leaving NAT
statements containing variables untouched.

## High-value set and map features

### Type queue and conntrack object maps

A `typeof` map may use `queue` as its value type, allowing a concatenated packet
key to select an NFQUEUE number. Object-reference maps can select conntrack
helpers, timeouts, or expectations:

```nft
map helpers {
    type inet_service : ct_helper
    elements = { 21 : "ftp-standard" }
}
ct helper set tcp dport map @helpers
```

### Bound packet-path updates

Sets updated from rules need explicit bounded storage:

```nft
set recent_sources {
    type ipv4_addr
    flags dynamic, timeout
    timeout 5m
    gc-interval 30s
    size 65536
}
```

Do not combine `dynamic` with `interval`. Expired entries still occupy capacity
until garbage collection.

### Preserve remaining lifetime during replication

Specify both `timeout` and `expires` when restoring an element whose remaining
lifetime matters:

```nft
add element inet filter recent_sources {
    192.0.2.10 timeout 1h expires 12m
}
```

`reset rules`, `reset set`, and `reset map` clear attached state without
removing their containers.

## High-value lifecycle and hook features

### Prefer idempotent destroy for cleanup

`destroy` works for tables, chains, rules, sets, maps, elements, flowtables, and
named stateful objects, and succeeds when the target is already absent:

```nft
destroy table inet stale
destroy element inet filter blocked { 192.0.2.1 }
```

Use it for convergent cleanup. Keep `delete` when absence should be reported.

### Manage table ownership and dormancy

The `owner` table flag prevents other processes from modifying a table and
normally removes it when the owner exits. Add `persist` to retain the orphaned
table. `dormant` unregisters base chains until the existing table is added again
without that flag.

### Use hook-device wildcards deliberately

Ingress and egress base chains and flowtables may use a trailing `*` in an
interface name on supporting kernels. `list hooks` shows actual attachments.
Existing `inet` ingress chains can update their device membership.

Remember packet order:

- ingress: network taps, tc ingress, then netfilter ingress;
- egress: netfilter egress, then tc egress.

A tc-ingress redirect skips both netfilter ingress and netfilter egress. A
netfilter-ingress redirect remains subject to netfilter egress.

### Treat rule indexes as snapshots

Indexes are zero-based and resolved to handles in userspace. Concurrent rule
changes can alter the effective position. At a location, `add` places a rule
after it and `insert` places a rule before it.

## Validation checklist

- Confirm kernel support before using compound bitwise assignment expressions
  or hook-device wildcards.
- Guard raw transport and inner-header reads with explicit outer protocol
  matches.
- Keep XOR right operands constant and binary-operation chains within the fixed
  limit.
- Give packet-updated sets `dynamic`, `timeout`, `size`, and a practical
  `gc-interval`.
- Accept both historical scalar and current array forms when consuming JSON
  flags.
- Treat normalized listings as semantically equivalent even when they add
  quoting, counts, default bursts, dependencies, or one-line complex elements.
- Check the host `route_localnet` sysctl when local-route behavior matters.
- Use handles rather than indexes when concurrent mutation is possible.
- Add required include directories explicitly in libnftables embedders.
- Verify release archives with the release-specific signature and digest.
