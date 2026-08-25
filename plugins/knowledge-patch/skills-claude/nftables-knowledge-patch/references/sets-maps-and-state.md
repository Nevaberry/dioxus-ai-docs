# Sets, Maps, and Stateful Data

## Type derivation and map values

Maps can derive an NFQUEUE-number value with `: queue` (since 1.1.2) and select
the queue from a concatenated key:

```nft
map get_queue_id {
    typeof ip saddr . ip daddr . tcp dport : queue
    elements = { 127.0.0.1 . 127.0.0.2 . 22 : 2 }
}
queue flags bypass to ip saddr . ip daddr . tcp dport map @get_queue_id
```

JSON input can use `typeof` for set and map types (since 1.1.2). A JSON
concatenation must have at least two expressions, and stateful statements are
permitted only on set elements.

Object-reference maps can contain conntrack helpers, timeouts, or expectations
and may use `typeof` keys (since 1.0.6.1):

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

Typed mappings can supply the NAT address family and interval-valued mappings
expand to ranges (since 1.0.6.1), which is especially useful in `inet` tables:

```nft
map targets {
    type ipv4_addr : ipv4_addr
    elements = { 192.0.2.10 : 10.0.0.10 }
}
dnat to ip daddr map @targets
```

## Intervals, aggregation, and auto-merge

Auto-merge is limited to singleton interval sets and skips elements with a
timeout or expiration (since 1.1.2). Timed adjacent intervals remain distinct.

`get element` returns the containing interval for interval sets and maps, and
`reset element` works with interval objects (since 1.1.2):

```console
nft get element x y '{ 1.1.1.2 }'
nft reset element inet filter intervalset '{ 1.2.3.4 }'
```

Range aggregation in concatenated sets retains the correct datatype in 1.1.5,
preventing incorrect evaluation when ranges are combined.

## Timeouts and garbage collection

Timeout-enabled maps accept `gc-interval` in 1.0.6.1, matching set syntax:

```nft
map sessions {
    type ipv4_addr : verdict
    flags timeout
    timeout 10m
    gc-interval 30s
}
```

Conntrack timeout policies accept time units rather than only bare numbers
(since 1.0.6.1):

```nft
ct timeout web-timeout {
    protocol tcp
    l3proto ip
    policy = { established : 2h, close : 10s }
}
```

Packet-path set updates require bounded storage as documented in 1.1.6-guide.
Declare `dynamic` and `timeout`, configure both a maximum `size` and a
`timeout`, and do not combine `dynamic` with `interval`:

```nft
set recent_sources {
    type ipv4_addr
    flags dynamic, timeout
    timeout 5m
    gc-interval 30s
    size 65536
}
```

Expired entries consume capacity until garbage collection. A long
`gc-interval` can therefore block new insertions even when old entries have
expired.

For ruleset replication, an element may carry its configured `timeout` and its
current remaining `expires` value (documented in 1.1.6-guide):

```nft
add element inet filter recent_sources { 192.0.2.10 timeout 1h expires 12m }
```

## Counters, limits, and resets

Set listings append the live element count to the configured maximum size
(since 1.1.4):

```nft
size 65535 # count 1
```

Set elements containing mappings, timeouts, comments, counters, quotas, or
limits are rendered on one line in listings (since 1.1.2).

Byte-rate limits accept a zero burst in 1.0.6.1. Listings print the default
burst when it was omitted, so normalized output may add an explicit value:

```nft
limit rate 1 mbytes/second burst 0 bytes accept
```

`reset rules` clears rule-contained counters and quotas at an optional family,
table, or chain scope. Resetting a set or map clears state on all elements but
does not remove the container (documented in 1.1.6-guide):

```nft
reset rules inet filter input
reset set inet filter recent_sources
```

Named maps can be deleted by handle in 1.1.4, matching sets:

```nft
delete map t handle 4000
```

