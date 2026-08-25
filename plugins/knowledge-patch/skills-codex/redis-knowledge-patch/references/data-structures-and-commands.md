# Data Structures and Commands

Use this reference for command behavior involving strings, hashes, lists,
sets, streams, notifications, and probabilistic structures.

## Arrays and compact hashes

Redis 8.8 adds Array as a data structure.

Redis 8.10 adds a compact hash encoding that stores shared field names once
for keys with the same schema, reducing memory for repeated hash shapes. The
new `HIMPORT` command provides high-throughput bulk insertion for compact
hashes. This compact-hash guidance comes from batch `8.10.0`.

## String compare, delete, and multi-key writes

Redis 8.4 adds `DIGEST` and `DELEX`, plus `SET` extensions, for atomic
compare-and-set and compare-and-delete operations on string keys.

`MSETEX` atomically sets multiple string keys and updates their expiration.
Redis 8.4.4 fixes an ACL key-pattern bypass in this command; apply that floor
before granting access.

## Window counters with `INCREX`

Redis 8.8 adds `INCREX`. It combines the behavior of `INCR`, `INCRBY`, and
`INCRBYFLOAT` with bounds and expiration, making it suitable for window-counter
rate limiting without a multi-command race.

## Multi-element list moves

`LMOVEM` moves multiple elements between lists. `BLMOVEM` supplies the
blocking form.

## Set and sorted-set aggregation

`SUNIONCARD` returns the cardinality of the union of multiple sets, while
`SDIFFCARD` returns the cardinality of their difference.

In Redis 8.8, `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and `ZINTERSTORE` accept the
`COUNT` aggregator.

## Additional `BITOP` operators

Redis 8.2 adds `DIFF`, `DIFF1`, `ANDOR`, and `ONE` to `BITOP`.

## Stream deletion reference controls

Redis 8.2 introduces `XDELEX` and `XACKDEL` and extends `XADD` and `XTRIM`.
The deletion controls include `DELREF` and `ACKED` reference strategies.

## Claim pending entries while reading new ones

Redis 8.4 adds `CLAIM min-idle-time` to `XREADGROUP`. One read can consume both
sufficiently idle pending entries and incoming entries.

## Idempotent stream production

Redis 8.6 adds `IDMPAUTO` and `IDMP` to `XADD` for at-most-once production.
`stream-idmp-duration` and `stream-idmp-maxsize` provide defaults.

Redis 8.6.0 warns against using those options with both `appendonly yes` and
`aof-use-rdb-preamble no`. Redis 8.6.2 fixes AOF rewrite and state restoration
for idempotency state.

## Explicit release of pending messages

Redis 8.8 adds `XNACK`, allowing a stream consumer to release pending messages
explicitly.

## Bounded stream reads

`XREAD` and `XREADGROUP` accept `MAXCOUNT` and `MAXSIZE`. `MAXCOUNT` caps the
cumulative number of entries in a reply; `MAXSIZE` caps cumulative reply size.

## Keyspace and hash-field notifications

Redis 8.2 adds `OVERWRITTEN` for complete value replacement and `TYPE_CHANGED`
for a key type change.

Redis 8.8 adds hash subkey notifications, enabling field-level notification
events rather than only key-level events.

## Cuckoo Filter failover durability

Redis 8.2.8, 8.4.5, and 8.6.5 replicate `CF.LOADCHUNK` chunks. Use one of these
fixed maintenance releases for the deployed line to prevent silent Cuckoo
Filter loss after failover. This maintenance guidance originates in source
batch `8.0-8.6`.
