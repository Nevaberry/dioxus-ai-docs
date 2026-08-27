# Search, JSON, and Time Series

Use this reference for vector and hybrid queries, Search configuration, JSON
array representation, and Time Series command behavior.

## Vector Set result and distance controls

Redis 8.0.3 adds `WITHATTRIBS` to `VSIM`, which returns an element's JSON
attribute. Redis 8.0.4 adds `EPSILON`, which sets a maximum distance.

## Compressed vector indexes

Redis 8.2 adds the compressed `SVS-VAMANA` vector-index type. Redis 8.2.2
allows the `BUILD_INTEL_SVS_OPT` build flag for Intel optimizations.

The proprietary LeanVec and LVQ Intel optimizations are absent from Redis Open
Source starting in 8.2.1. Remove assumptions that those optimizations are
available when selecting an index or build configuration.

## Hybrid search and fused scoring

Redis 8.4 adds `FT.HYBRID` with RRF and LINEAR result combination. In the
original 8.4 behavior:

- filtering after `COMBINE` is unavailable;
- the default response contains only `key_id` and `score`; and
- `EXPLAINSCORE`, `YIELD_DISTANCE_AS`, and `WITHCURSOR` are unsupported.

The newer `KNN` clause accepts an argument that requests fewer candidates per
shard. `FT.PROFILE HYBRID` adds profiling for `FT.HYBRID` queries. These two
later hybrid-query additions are from source batch `8.8.1`.

## Default Search scorer

`search-default-scorer` configures the default text and tag scorer. `BM25STD`
is the new default on the 8.4 line.

## Search aliases, stemming, and schema validation

`FT.ALIASLIST` returns every alias for an index. Search also supports stemming
for Malay and Tagalog.

`FT.CREATE` and `FT.ALTER` reject an empty string as a field name rather than
silently accepting it. These Search command changes are attributed to batch
`8.10.0`.

## Homogeneous floating-point JSON arrays

`JSON.SET` accepts `FPHA`, which specifies the floating-point type for a
homogeneous floating-point array.

## Multiple Time Series aggregators

`TS.RANGE`, `TS.REVRANGE`, `TS.MRANGE`, and `TS.MREVRANGE` can apply multiple
aggregators in one command.

## NaN values and aggregators

Redis 8.6 allows NaN values in Time Series and adds `COUNTNAN` and `COUNTALL`.
Account for NaN explicitly in aggregation and result handling.

## Timestamp-grouped multi-series ranges

`TS.NRANGE` and `TS.NREVRANGE` query ranges across multiple time series and
group the results by timestamp.

## Blocking Time Series reads

`TS.READ` reads from time series and supports optional blocking behavior.

## Label discovery

`TS.QUERYLABELS` returns labels and their label values.

## Excluding empty series

`TS.MRANGE` and `TS.MREVRANGE` accept `EXCLUDEEMPTY`, which omits series that
report no samples.

## Cluster migration caveat

During `CLUSTER MIGRATION`, the Search and Time Series multi-key queries
identified by the release notes can return partial or duplicate results.
Atomic slot movement does not make these query results atomic.
