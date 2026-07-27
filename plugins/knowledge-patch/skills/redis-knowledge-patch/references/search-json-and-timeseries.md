# Search, JSON, and Time Series

Use this reference when creating vector indexes, combining text and vector
queries, profiling hybrid searches, storing homogeneous floating-point arrays,
or aggregating Time Series data.

## Vector Set query controls

`VSIM` gains controls in early Redis 8 maintenance releases:

- `WITHATTRIBS` returns an element's JSON attribute starting in 8.0.3.
- `EPSILON` sets a maximum distance starting in 8.0.4.

Vector Set remains marked preview in the integrated component distribution.

## Compressed vector indexes

Redis 8.2 adds the compressed `SVS-VAMANA` vector-index type. Redis 8.2.2
allows the `BUILD_INTEL_SVS_OPT` build flag for Intel optimizations.

The proprietary LeanVec and LVQ Intel optimizations were removed from Redis
Open Source in 8.2.1. Do not preserve build or deployment assumptions that
depend on those removed implementations.

## Hybrid search and fused scoring

Redis 8.4 adds `FT.HYBRID` with two result-combination methods:

- RRF
- LINEAR

The original 8.4 behavior has important limitations:

- Filtering after `COMBINE` is unavailable.
- The default response contains only `key_id` and `score`.
- `EXPLAINSCORE` is unsupported.
- `YIELD_DISTANCE_AS` is unsupported.
- `WITHCURSOR` is unsupported.

Redis 8.8 extends the `KNN` clause with an argument that requests fewer
candidates per shard. `FT.PROFILE HYBRID` adds profiling for `FT.HYBRID`
queries.

## Default Search scorer

The 8.4 line adds `search-default-scorer` for selecting the default text and tag
scorer. `BM25STD` is the new default.

## Search ACL boundary

An ACL user can create, modify, or read a Search index only when the user's key
patterns cover a superset of the index prefixes. This condition is separate
from membership in the broader or component-specific command categories.

## Homogeneous floating-point JSON arrays

Redis 8.8 adds `FPHA` to `JSON.SET`. The argument specifies the floating-point
type for a homogeneous floating-point array.

## Multiple Time Series aggregators

Redis 8.8 lets these commands apply multiple aggregators in one operation:

- `TS.RANGE`
- `TS.REVRANGE`
- `TS.MRANGE`
- `TS.MREVRANGE`

## NaN handling and counts

Redis 8.6 permits NaN Time Series values and adds two aggregators:

- `COUNTNAN`
- `COUNTALL`

## Time Series ACL boundary

`TS.MGET`, `TS.MRANGE`, and `TS.MREVRANGE` return an error when any matching
key is unreadable. `TS.QUERYINDEX` operates on metadata and does not require
read permission for the keys it matches.

These Search, JSON, and Time Series changes are drawn from batches `8.0-8.6`
and `8.8.1`; the sections remain grouped by developer task.
