# Compatibility and Deployment

This reference organizes build and hosting guidance from `current-reference`
and `hosted-deployment`.

## Check PostgreSQL compatibility first

pgvector 0.8 does not support PostgreSQL 12. Upgrade the database server before
adopting the pgvector 0.8 line.

On Windows, pgvector builds against PostgreSQL 17.0 through 17.2 can fail with
an unresolved `float_to_shortest_decimal_bufn` symbol. Upgrade to PostgreSQL
17.3 or newer before building.

## Select a published artifact

Source-build instructions pin pgvector 0.8.5. Versioned Docker tags support
PostgreSQL 13 through 18 and offer Bookworm and Trixie variants.

```shell
docker pull pgvector/pgvector:0.8.5-pg18-trixie
```

Homebrew installs pgvector only for the `postgresql@17` and `postgresql@18`
formulas. Check the local PostgreSQL formula before relying on that package.

## Build a portable extension

Some build platforms enable `-march=native`. An extension compiled this way
can fail with `Illegal instruction` after it is moved to a processor with a
different instruction set. Clear the optimization flags when the artifact
must be portable:

```shell
make OPTFLAGS=""
```

## Allocate Docker shared memory for HNSW builds

A parallel HNSW build can fail when a raised `maintenance_work_mem` exceeds
the container's shared-memory allocation. Set `--shm-size` to at least the
same size as `maintenance_work_mem`.

```shell
docker run --shm-size=1g ...
```

## Choose an extension version on Neon

Neon provides its latest supported pgvector release and the immediately
previous published release. To use the older release, first determine its
actual version; do not simply decrement the latest version number because
pgvector releases are not always sequential. Then request it explicitly:

```sql
CREATE EXTENSION vector VERSION '0.7.4';
```

## Size approximate-index builds on Neon

Neon's default `maintenance_work_mem` varies with compute size. For an HNSW or
IVFFlat build, set the value for the session to approximately the vector-index
working-set size while keeping it below about 50–60% of available RAM.

`max_parallel_maintenance_workers` defaults to `2`. It can be raised toward
the compute's CPU count, but remains constrained by `max_parallel_workers` and
`max_worker_processes`.

```sql
SET maintenance_work_mem = '10 GB';
SET max_parallel_maintenance_workers = 7;
```
