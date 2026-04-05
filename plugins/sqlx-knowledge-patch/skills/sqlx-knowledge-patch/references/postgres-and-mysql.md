# Postgres & MySQL

## Postgres Geometry Types

Native Postgres geometric type support added incrementally:

### 0.8.3
- `PgPoint` — Postgres `POINT` type
- `PgLine` — Postgres `LINE` type

### 0.8.4
- `PgLineSegment` — Postgres `LSEG` type
- `PgBox` — Postgres `BOX` type
- `PgPath` — Postgres `PATH` type
- `PgPolygon` — Postgres `POLYGON` type
- `PgCircle` — Postgres `CIRCLE` type

## `ipnet` Support (0.8.4+)

`ipnet::IpNet` maps to Postgres `INET`/`CIDR` types (requires `ipnet` feature):

```toml
[dependencies]
sqlx = { version = "0.8", features = ["ipnet"] }
```

## `PgConnectOptions::options()` Auto-Escaping (0.9)

Options passed to `PgConnectOptions::options()` are now automatically escaped. Remove any manual escaping to avoid double-escaping.

## `PgListener` Improvements (0.8.3+)

`PgListener` now implements `Acquire`, allowing it to be used where a connection is needed. New `next_buffered()` method supports batch processing of notifications without awaiting each one individually.

## MySQL Collation Inference Change (0.9)

Text columns previously inferred as `Vec<u8>` are now inferred as `String`. Additional changes:
- `SET NAMES utf8mb4` is sent without specifying collation
- `charset()` and `collation()` now imply `set_names(true)`
