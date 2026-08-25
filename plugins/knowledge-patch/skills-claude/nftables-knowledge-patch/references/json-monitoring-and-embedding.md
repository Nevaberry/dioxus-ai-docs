# JSON, Monitoring, and Embedding

## JSON flag compatibility

In 1.1.4, a single JSON `flags` value was emitted as a scalar string, including
sets plus `fib` and `synproxy` expressions:

```json
{ "flags": "interval" }
```

That shape was superseded in 1.1.5. JSON output and monitor events preserve a
one-item array, which is the current form:

```json
{ "flags": ["interval"] }
```

Historical-output readers can accept both shapes. New generators should emit
the array.

## JSON ruleset coverage

JSON supports `typeof` types for sets and maps in 1.1.2. Concatenations must
contain at least two expressions, and stateful statements are allowed only on
set elements.

Relational FIB expressions serialize to JSON again in 1.1.5.

The interface added broader native coverage in 1.0.6.1:

- Table and chain comments.
- Set `dynamic` and `auto-merge` options.
- Map statements and maps with concatenated data.
- Synproxy objects.
- Multi-device chain hooks.
- Binary expressions with more than two operands.

```json
{ "add": { "table": { "family": "inet", "name": "filter", "comment": "managed" } } }
```

Tunnel objects and their statements can be represented in JSON in 1.1.6.

## Monitor and trace streams

Flowtable add and delete events are visible to `nft monitor` since 1.1.2.

Trace output includes conntrack records in 1.1.4 when the data is present. A
record can carry direction, state, ID, and status:

```console
trace id 32 t INPUT conntrack: ct direction original ct state new ct status dnat-done ct id 2641368242
```

Text monitor output quotes device names in chain declarations in 1.1.6. JSON
monitor output identifies object-delete events with the corrected event type.
Consumers should accept the quoted text and use the corrected deletion event.

## Netlink batch handling

Batch processing continues after an `ENOBUFS` error in 1.1.5 instead of
stopping at that condition. Callers should still report and handle the error,
but must not assume it terminated processing of the remaining batch.

## Embedding include paths

As of 1.1.6, libnftables no longer restores its default include directory after
the caller replaces the include search path. Embedders that still require the
default directory must add it explicitly along with their custom paths.

