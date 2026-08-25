# Search, JSON, and Time Series

## Vector Set result controls

Redis 8.0.3 adds `WITHATTRIBS` to `VSIM`, returning an element's JSON
attribute. Redis 8.0.4 adds `EPSILON`, which sets a maximum distance.

## Compressed vector indexes

Redis 8.2 adds the compressed `SVS-VAMANA` vector-index type. Redis 8.2.2
allows the `BUILD_INTEL_SVS_OPT` build flag for Intel optimizations.

Do not plan around proprietary LeanVec or LVQ Intel optimizations: they were
removed from Redis Open Source in 8.2.1.

## Hybrid search and fused scoring

Redis 8.4 adds `FT.HYBRID`, supporting RRF and LINEAR result combination. In
the original 8.4 behavior:

- filtering after `COMBINE` is unavailable;
- the default response contains only `key_id` and `score`; and
- `EXPLAINSCORE`, `YIELD_DISTANCE_AS`, and `WITHCURSOR` are unsupported.

The `KNN` clause later gains an argument that requests fewer candidates per
shard. `FT.PROFILE HYBRID` profiles `FT.HYBRID` queries. These additions are
recorded in batch `8.8.1`.

## Search scorer configuration

The Redis 8.4 line adds `search-default-scorer` for choosing the default text
and tag scorer. `BM25STD` is the new default.

## Alias enumeration and language stemming

Redis 8.10 adds `FT.ALIASLIST`, which returns all aliases for an index. Search
also gains stemming support for Malay and Tagalog.

## Empty field-name rejection

Redis 8.10 changes `FT.CREATE` and `FT.ALTER` to reject an empty string as a
field name instead of silently accepting it. Validate generated schemas and
migration input before sending either command.

## Homogeneous floating-point JSON arrays

Redis 8.8 extends `JSON.SET` with `FPHA`. The argument specifies the
floating-point type used by a homogeneous floating-point array.

## Multiple Time Series aggregators

Redis 8.8 lets `TS.RANGE`, `TS.REVRANGE`, `TS.MRANGE`, and `TS.MREVRANGE`
apply multiple aggregators in one command.

## NaN handling

Redis 8.6 accepts NaN values in Time Series and adds the `COUNTNAN` and
`COUNTALL` aggregators. Code that previously assumed every stored sample was a
regular number must handle NaN explicitly.

## Timestamp-grouped range queries

Redis 8.10 adds `TS.NRANGE` and `TS.NREVRANGE`. They query ranges across
multiple time series and group results by timestamp.

## Blocking Time Series reads

Redis 8.10 adds `TS.READ`, including optional blocking reads from time series.
Treat the blocking form as a connection-management concern in clients and
connection pools.

## Label discovery

Redis 8.10 adds `TS.QUERYLABELS`, which returns labels and their label values.

## Excluding empty series

Redis 8.10 extends `TS.MRANGE` and `TS.MREVRANGE` with `EXCLUDEEMPTY`, omitting
series that report no samples.

The Redis 8.10 Search and Time Series additions in this reference derive from
the `8.10.0` batch.
