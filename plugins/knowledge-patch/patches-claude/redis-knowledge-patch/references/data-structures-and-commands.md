# Data Structures and Commands

## Array data structure

Redis 8.8 adds Array as a data structure. This item comes from batch `8.8.1`.

## Compact hashes and bulk import

Redis 8.10 adds a compact hash encoding that stores shared field names once for
keys with the same schema. Use it to reduce memory for repeated hash shapes.
`HIMPORT` supplies high-throughput bulk insertion for compact hashes.

## Atomic string operations

Redis 8.4 adds `DIGEST`, `DELEX`, and `SET` extensions for atomic
compare-and-set and compare-and-delete operations on string keys.

`MSETEX` atomically sets multiple string keys and updates their expiration.
When using it on older 8.4 deployments, account for the ACL key-pattern bypass
fixed in 8.4.4.

## Window counters

Redis 8.8 adds `INCREX`. It combines the behavior of `INCR`, `INCRBY`, and
`INCRBYFLOAT` with bounds and expiration, making an atomic window-counter
primitive for rate limiting.

## Multi-element list moves

Redis 8.10 adds `LMOVEM` and `BLMOVEM` to move multiple elements between
lists. `BLMOVEM` is the blocking form.

## Set-operation cardinality

Redis 8.10 adds `SUNIONCARD` for the cardinality of a union across multiple
sets and `SDIFFCARD` for the cardinality of their difference.

## Stream deletion references

Redis 8.2 adds `XDELEX` and `XACKDEL` and extends `XADD` and `XTRIM`. The new
deletion controls include `DELREF` and `ACKED` reference strategies.

## Claim while reading

Redis 8.4 adds `CLAIM min-idle-time` to `XREADGROUP`. One read can return both
sufficiently idle pending entries and incoming entries.

## Idempotent stream production

Redis 8.6 adds `IDMPAUTO` and `IDMP` to `XADD` for at-most-once production.
`stream-idmp-duration` and `stream-idmp-maxsize` provide defaults.

Do not overlook persistence history:

- Redis 8.6.0 warns against using the options with `appendonly yes` and
  `aof-use-rdb-preamble no`.
- Redis 8.6.2 fixes AOF rewrite and state restoration for idempotency state.

## Explicitly releasing pending messages

Redis 8.8 adds `XNACK`, which lets a stream consumer explicitly release
pending messages.

## Bounded stream reads

Redis 8.10 extends `XREAD` and `XREADGROUP` with:

- `MAXCOUNT`, which caps the cumulative number of returned entries; and
- `MAXSIZE`, which caps the cumulative reply size.

These limits apply to the overall reply rather than independently to each
stream.

## Additional bit operations

Redis 8.2 extends `BITOP` with `DIFF`, `DIFF1`, `ANDOR`, and `ONE`.

## Sorted-set `COUNT` aggregation

Redis 8.8 adds the `COUNT` aggregator to `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and
`ZINTERSTORE`.

## Keyspace and hash-field notifications

Redis 8.2 adds `OVERWRITTEN` for complete value replacement and `TYPE_CHANGED`
for a key type change.

Redis 8.8 adds hash subkey notifications, allowing field-level events rather
than only whole-key notifications.

## Cuckoo Filter failover durability

In Redis 8.2.8, 8.4.5, and 8.6.5, `CF.LOADCHUNK` chunks are replicated. These
maintenance fixes prevent silent loss of Cuckoo Filter data after failover.

This reference includes command work from the `8.0-8.6` batch as well as the
later structures and commands described above.
