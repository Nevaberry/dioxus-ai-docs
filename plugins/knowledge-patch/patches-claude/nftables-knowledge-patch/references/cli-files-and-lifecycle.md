# CLI, Files, and Ruleset Lifecycle

## Listing and error behavior

The short table-scoped set listing form is accepted since 1.1.2:

```console
nft list sets inet foo
```

The older form was `list sets table inet foo`.

Both native and JSON commands return an error when a requested table does not
exist (since 1.1.2). Extended netlink errors for large set elements preserve the
correct source location.

## Includes and file targets

Equivalent include paths are canonicalized so the same file is not included
twice through different spellings (since 1.1.2).

The include rules documented in 1.1.6-guide are deterministic:

- Include paths use directories supplied by `-I` or `--includepath`.
- A leading `./` forces resolution from the current directory.
- A leading `/` selects an absolute path.
- Wildcard matches load in C-locale collation order.
- Wildcards ignore dotfiles.
- A wildcard that matches nothing is not an error.

```nft
include "/etc/firewall/rules.d/*.nft"
```

Libnftables output targets must be regular files or named pipes, and include
targets must be regular files (since 1.0.6.1). `/dev/stdin` remains a valid
automation input.

## Symbolic variables

Variables are block-scoped and mutable as documented in 1.1.6-guide. A
definition is visible in its block and nested blocks, and a variable reference
is an expression that can initialize another variable. Use `redefine` to change
a definition and `undefine` to remove it:

```nft
define uplink = eth0
redefine uplink = wlan0
undefine uplink
```

## Idempotent removal

`destroy` commands do not fail when the target is absent (documented in
1.1.6-guide). They cover tables, chains, rules, sets, maps, elements,
flowtables, and named stateful objects:

```nft
destroy table inet stale
destroy element inet filter blocked { 192.0.2.1 }
```

Use `delete` when a missing target should be reported as an error. For maps,
handle-based deletion is also supported:

```nft
delete map t handle 4000
```

## Rule placement

Rule indexes are zero-based and resolved to handles in userspace before the
request reaches the kernel (documented in 1.1.6-guide). Concurrent insertions
or deletions can therefore change the effective indexed position.

When a location is supplied, `add` places the new rule after that location,
whereas `insert` places it before. Use handles when a concurrent editor makes
an index unsafe.

