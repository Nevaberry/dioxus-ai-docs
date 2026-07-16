# Compatibility and Deployment

## PostgreSQL and pgvector versions

PostgreSQL 12 support was removed in pgvector 0.8. Upgrade to PostgreSQL 13 or
newer before adopting the release. Current source-build instructions pin
pgvector 0.8.5.

The published pgvector container matrix spans PostgreSQL 13 through 18 and
includes versioned Bookworm and Trixie tags.

```sh
docker pull pgvector/pgvector:0.8.5-pg18-trixie
```

## Portable source builds

Some platforms compile pgvector with `-march=native`. A resulting extension can
fail with an illegal-instruction error when it runs on a machine with a
different CPU. Clear `OPTFLAGS` when the build artifact must be portable.

```sh
make OPTFLAGS=""
```

## Shared memory for containerized HNSW builds

Parallel HNSW construction uses PostgreSQL maintenance memory. In Docker, make
container shared memory at least as large as `maintenance_work_mem`.

```sh
docker run --shm-size=1g ...
```

## Hosted extension version windows

Neon makes its latest supported pgvector release and exactly one prior release
available. To use the prior release, install it explicitly. pgvector release
numbers are not guaranteed to be sequential, so identify the previously
published version rather than decrementing the newest version number.

```sql
CREATE EXTENSION vector VERSION '0.7.4';
```

## Compute-aware approximate-index builds

On Neon, the default `maintenance_work_mem` varies with compute size. For HNSW
or IVFFlat construction, set it for the session to approximately the vector
index's working-set size, without exceeding roughly 50–60% of available RAM.

`max_parallel_maintenance_workers` defaults to `2`. It can be raised toward the
compute's CPU count, but remains constrained by `max_parallel_workers` and
`max_worker_processes`.

```sql
SET maintenance_work_mem = '10 GB';
SET max_parallel_maintenance_workers = 7;
```
