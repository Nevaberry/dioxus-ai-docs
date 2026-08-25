# JSON, monitoring, and automation

Use this reference when consuming JSON, watching live events, embedding
libnftables, or composing modular rulesets.

## JSON `typeof` and validation (1.1.2)

JSON input can specify `typeof` set and map types. Concatenations require at
least two expressions, and stateful statements are valid only on set elements.
Native and JSON commands both report an error when the requested table is
absent.

## Flag shape across releases (1.1.4, 1.1.5)

The 1.1.4 output shape reduced one `flags` value to a scalar, including on sets
and `fib` and `synproxy` expressions:

```json
{ "flags": "interval" }
```

The 1.1.5 behavior supersedes that shape and preserves a one-item array,
including in monitor output:

```json
{ "flags": ["interval"] }
```

Cross-version consumers should accept both. New output should use the array.

## Expanded JSON coverage (1.0.6.1, 1.1.5, 1.1.6)

Relational FIB expressions serialize to JSON. JSON commands and output also
cover:

- table and chain comments;
- set `dynamic` and `auto-merge` options;
- map statements and maps with concatenated data;
- synproxy objects;
- multi-device chain hooks;
- binary expressions containing more than two operands;
- VXLAN, ERSPAN, and Geneve tunnel objects with their statements.

```json
{
  "add": {
    "table": {
      "family": "inet",
      "name": "filter",
      "comment": "managed"
    }
  }
}
```

JSON monitor output identifies object-delete events with the corrected event
type.

## Flowtable and trace monitoring (1.1.2, 1.1.4)

`nft monitor` recognizes flowtable add and delete events.

`nft monitor trace` emits a `conntrack:` record when connection tracking data is
present. It can include direction, state, ID, and status:

```console
trace id 32 t INPUT conntrack: ct direction original ct state new ct status dnat-done ct id 2641368242
```

## Text monitor compatibility (1.1.6)

Text monitor output quotes device names in chain declarations. Consumers should
accept the quoted form. JSON consumers should use the corrected object-delete
event rather than compensating for the earlier misidentification.

## Include resolution and globs (1.1.2, 1.1.6-guide)

Equivalent include paths are canonicalized, preventing duplicate inclusion.

Include lookup follows these rules:

- `-I` or `--includepath` supplies search directories;
- a leading `./` forces the current directory;
- a leading `/` selects an absolute path;
- wildcard matches load in C-locale collation order;
- wildcard matches ignore dotfiles;
- a wildcard that matches nothing is not an error.

```nft
include "/etc/firewall/rules.d/*.nft"
```

## Libnftables include paths and file targets (1.0.6.1, 1.1.6)

Libnftables output paths must resolve to a regular file or named pipe. Include
targets must be regular files. `/dev/stdin` remains accepted as an automation
input.

The library no longer restores its default include directory after an embedder
replaces the include search path. Add that directory explicitly when needed.

## Symbolic variables (1.1.6-guide)

A definition is visible in its block and nested blocks. Variable references are
expressions and can initialize other variables. Use `redefine` to change a
definition and `undefine` to remove it:

```nft
define uplink = eth0
redefine uplink = wlan0
undefine uplink
```

## Netlink batch resilience (1.1.5)

Batch processing continues after an `ENOBUFS` error. Automation should still
report and diagnose the condition, but must not assume it terminates processing
of the remaining batch.
