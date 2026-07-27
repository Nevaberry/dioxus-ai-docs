# Data Structures and Commands

Use this reference when implementing counters, atomic string changes, stream
production and consumption, notifications, bit operations, sorted-set
combinations, or Cuckoo Filter restore flows.

## Array and window counters

Redis 8.8 adds Array as a data structure.

`INCREX` combines the behavior needed for window-counter rate limiting:

- `INCR`, `INCRBY`, or `INCRBYFLOAT`-style increments;
- lower or upper bounds; and
- expiration.

## Atomic string operations

Redis 8.4 adds `DIGEST` and `DELEX` and extends `SET` for atomic
compare-and-set and compare-and-delete operations on string keys.

`MSETEX` atomically sets multiple string keys and updates their expiration. If
using it on an older 8.4 maintenance release, account for the ACL key-pattern
bypass fixed in 8.4.4.

## Stream deletion and references

Redis 8.2 adds `XDELEX` and `XACKDEL` and extends `XADD` and `XTRIM`. The stream
deletion controls include these reference strategies:

- `DELREF`
- `ACKED`

Before enabling the new commands on untrusted input, account for the
`XACKDEL` stack-overflow/RCE fix in 8.2.3.

## Reading and releasing pending stream entries

Redis 8.4 adds `CLAIM min-idle-time` to `XREADGROUP`. One read can claim and
return pending entries whose idle time is high enough while also consuming new
entries.

Redis 8.8 adds `XNACK`, which lets a stream consumer explicitly release pending
messages.

## Idempotent stream production

Redis 8.6 adds `IDMPAUTO` and `IDMP` to `XADD` for at-most-once production. The
configuration settings `stream-idmp-duration` and `stream-idmp-maxsize` provide
defaults.

Redis 8.6.0 warns against using these options when both conditions hold:

- `appendonly yes`
- `aof-use-rdb-preamble no`

Redis 8.6.2 fixes AOF rewrite and state-restoration problems involving the
idempotency state.

## Bit operations

Redis 8.2 adds four `BITOP` operators:

- `DIFF`
- `DIFF1`
- `ANDOR`
- `ONE`

## Sorted-set combinations

Redis 8.8 allows `ZUNION`, `ZINTER`, `ZUNIONSTORE`, and `ZINTERSTORE` to use the
`COUNT` aggregator.

## Keyspace and hash-field notifications

Redis 8.2 adds two keyspace notification events:

- `OVERWRITTEN` for complete replacement of a value;
- `TYPE_CHANGED` when a key's type changes.

Redis 8.8 adds hash subkey notifications, enabling field-level events.

## Cuckoo Filter failover durability

Redis 8.2.8, 8.4.5, and 8.6.5 replicate `CF.LOADCHUNK` chunks. Earlier affected
maintenance releases can silently lose restored Cuckoo Filter data on failover.

The command and data-structure changes above originate in the included
`8.0-8.6` and `8.8.1` batches; version-specific constraints are stated beside
the affected operation rather than organized as a release log.
