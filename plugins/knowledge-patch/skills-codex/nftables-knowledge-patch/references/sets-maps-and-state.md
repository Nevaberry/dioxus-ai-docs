# Sets, maps, and state

Use this reference when declaring containers, selecting objects, updating sets
from rules, or preserving state across replication.

## `typeof` sets and maps (1.1.2)

Maps can derive an NFQUEUE-number value type with `: queue` and select the queue
from a concatenated key:

```nft
map get_queue_id {
    typeof ip saddr . ip daddr . tcp dport : queue
    elements = { 127.0.0.1 . 127.0.0.2 . 22 : 2 }
}
queue flags bypass to ip saddr . ip daddr . tcp dport map @get_queue_id
```

JSON input can use `typeof` for set and map types. A JSON concatenation must
contain at least two expressions, and stateful statements are permitted only on
set elements. Text input rejects non-serializable `typeof` expressions.

## Intervals, auto-merge, and lookup (1.1.2, 1.1.5)

Auto-merge applies only to singleton interval sets and skips elements with a
timeout or expiration. Timed adjacent intervals remain separate.

`get element` returns the containing interval from an interval set or map.
`reset element` also works on interval objects:

```console
nft get element x y '{ 1.1.1.2 }'
nft reset element inet filter intervalset '{ 1.2.3.4 }'
```

Concatenated-set range aggregation retains the correct datatype.

## Listing and deleting containers (1.1.2, 1.1.4)

Normal set listings append the current element count to the configured maximum:

```nft
size 65535 # count 1
```

Elements containing mappings, timeouts, comments, counters, quotas, or limits
are printed on one line. Parsers must not require the older multiline shape.

Named maps can be deleted by handle:

```nft
delete map t handle 4000
```

## Timeout-enabled maps and object selection (1.0.6.1)

Timeout-enabled maps accept `gc-interval`:

```nft
map sessions {
    type ipv4_addr : verdict
    flags timeout
    timeout 10m
    gc-interval 30s
}
```

Object-reference maps may use `typeof` keys and contain conntrack helpers,
timeouts, or expectations. A rule can select one of those objects:

```nft
ct helper ftp-standard {
    type "ftp" protocol tcp
    l3proto ip
}
map helpers {
    type inet_service : ct_helper
    elements = { 21 : "ftp-standard" }
}
ct helper set tcp dport map @helpers
```

## Dynamic packet-path updates (1.1.6-guide)

A set updated from packet-path rules needs bounded storage:

- declare a maximum `size`;
- declare a `timeout`;
- state the `dynamic` and `timeout` capabilities explicitly;
- do not combine `dynamic` with `interval`;
- choose a `gc-interval` short enough that expired entries do not exhaust the
  set before collection.

```nft
set recent_sources {
    type ipv4_addr
    flags dynamic, timeout
    timeout 5m
    gc-interval 30s
    size 65536
}
```

Expired elements consume capacity until garbage collection. A long collection
interval can therefore block new insertions even though elements have expired.

## Replicating remaining lifetime (1.1.6-guide)

An element can carry its configured `timeout` and its current remaining
`expires` value. Restore both when replicating live state:

```nft
add element inet filter recent_sources {
    192.0.2.10 timeout 1h expires 12m
}
```

## Resetting attached state (1.1.6-guide)

`reset rules` clears rule-contained counters, quotas, and similar state at an
optional family, table, or chain scope:

```nft
reset rules inet filter input
```

Resetting a set or map clears state attached to all elements without deleting
the container:

```nft
reset set inet filter recent_sources
```
