# Compatibility and Deployment

## Require PostgreSQL 13 or newer

The pgvector 0.8 release line removes PostgreSQL 12 support. Upgrade the server
before installing or upgrading to that line.

Check the running server rather than relying only on client tools or package
names. An extension package being available does not make an unsupported
server version compatible.

## Choose a current release artifact

Current source-build instructions pin pgvector 0.8.5. Versioned container tags
cover PostgreSQL 13 through 18 on Bookworm and Trixie.

```shell
docker pull pgvector/pgvector:0.8.5-pg18-trixie
```

Select a tag whose pgvector version, PostgreSQL major version, and base
distribution all match the deployment. Homebrew installs the extension only
for its `postgresql@17` and `postgresql@18` formulas.

## Build portable native binaries

Some platforms compile with `-march=native`. Moving that artifact to a
processor without the same instruction set can cause an `Illegal instruction`
failure. Clear `OPTFLAGS` when the output must run on another machine.

```shell
make OPTFLAGS=""
```

Build on a toolchain compatible with the destination and test the resulting
extension on representative hardware.

## Provide Docker shared memory for HNSW builds

A parallel HNSW index build can fail when the container's shared-memory limit
is lower than an increased `maintenance_work_mem`. Set `--shm-size` to at least
the same size.

```shell
docker run --shm-size=1g ...
```

Keep the database setting and container allocation aligned when changing the
index-build budget.

## Avoid the early PostgreSQL 17 Windows linker failure

On Windows, builds against PostgreSQL 17.0 through 17.2 can fail because the
`float_to_shortest_decimal_bufn` symbol is unresolved. Upgrade PostgreSQL to
17.3 or newer before building the extension.

This is a build-toolchain compatibility issue; changing SQL or index settings
does not resolve it.

## Select a Neon extension version explicitly

Neon provides its latest supported pgvector release and the immediately
previous published release. To install the older one, name it explicitly:

```sql
CREATE EXTENSION vector VERSION '0.7.4';
```

Determine the actual previously published release instead of subtracting one
from the latest version number. pgvector release numbers are not guaranteed to
be sequential.

## Tune hosted approximate-index builds

Neon's default `maintenance_work_mem` varies with compute size. Before an HNSW
or IVFFlat build, set it for the session to approximately the vector index's
working-set size without exceeding roughly 50–60% of available RAM.

```sql
SET maintenance_work_mem = '10 GB';
```

`max_parallel_maintenance_workers` defaults to `2`. It can be raised toward
the compute's CPU count, but remains constrained by `max_parallel_workers` and
`max_worker_processes`.

```sql
SET max_parallel_maintenance_workers = 7;
```

Treat the numeric examples as sizing patterns, not universal values. Check the
compute's RAM, CPU count, and global worker settings before the index build.
