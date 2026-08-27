# CLI, Artifacts, and Runtime

## Quiet Command Results

In `1.9.0`, `dbt show` and `dbt compile` retain parseable JSON or text results
when run with `--quiet`. Automation can suppress event logs without losing the
command result.

## Empty and Sample Runs

Snapshots accept `--empty`, and Jinja code can inspect `flags.EMPTY`:

```jinja
{% if flags.EMPTY %}
  -- schema-only execution
{% endif %}
```

Core 1.10 introduces sample mode and enables it for `dbt build`. The final CLI
folds the separate `--sample-window` parameter into `--sample`. Sampling also
applies to referenced seeds and follows snapshot dependency graphs.

Core 1.12 adds empty seed relations. `dbt seed --empty` creates selected seed
tables without loading their rows:

```bash
dbt seed --empty --select customers
```

## Command Behavior

`dbt docs serve` accepts `--host` and defaults to `127.0.0.1`. Bind to an
external address, for example `--host 0.0.0.0`, only when generated docs must
be reachable beyond localhost.

`dbt deps`, `dbt clean`, and `dbt init` no longer change the process working
directory. Embedded callers must manage paths explicitly.

From Core 1.9.1, a `PartialSuccess` result returns a nonzero exit status. CI
checks must not assume that partial success exits zero.

Core 1.12 adds ad-hoc SQL through `dbt run-operation --sql`, without requiring
a wrapper macro. Macros invoked by `run-operation` may call `ref()` on private
and protected models.

```bash
dbt run-operation --sql 'select count(*) from {{ ref("orders") }}'
```

## Listing and Compilation Output

From `1.11.0`, `dbt ls --output json --output-keys` accepts nested key paths:

```bash
dbt ls --output json --output-keys name config.materialized
```

In `1.12.0`:

- `dbt compile` writes compiled snapshot SQL under `target/compiled/`.
- The Jinja `graph` includes unit tests.
- Python-model parsing recognizes `config.meta_get`.
- `NodeStatus` and `RunStatus` add `Reused`.
- Model records emitted by `dbt ls --output json` add runtime-only
  `direct_parents`, the nearest public ancestors. This field is not added to
  `manifest.json`.

## Artifacts, Logs, and Package Locks

Core `1.10.0` expands machine-readable metadata:

- Artifact metadata gains an invocation-start timestamp and quoting config.
- Manifest nodes and columns gain `doc_blocks`.
- Structured-log `node_info` gains `node_checksum`.
- Package lock entries gain `name`.
- Core can upload artifacts to dbt Cloud.

## Catalog File Loading

Core parses `catalogs.yml`; from 1.10.12 it also parses that file during
`parse`, `seed`, and `test`. Catalog integration configuration accepts
`file_format`.

With Core 1.12, every command that requires a manifest loads catalog
configuration. See the project-configuration reference for Catalog V2 and
database-name precedence.

## External V2 Parser

`--use-v2-parser` bypasses Core's parser, invokes an external parser, and loads
the resulting `manifest.json` into the runtime manifest. Choose the parser
command using `--v2-parser`, `DBT_ENGINE_V2_PARSER`, or project `flags`. The
default is `dbt-core-experimental-parser parse`.

```bash
dbt parse --use-v2-parser \
  --v2-parser "dbt-core-experimental-parser parse"
```

Core 1.12 initially requires `dbt-core-experimental-parser>=2.0.0a4`. The
`1.12.1` batch records a Core 1.12.2 increase to `2.0.0b1`.

## OpenTelemetry

Core 1.12.1 emits OpenTelemetry spans for node and hook execution when
`--snowflake-projects-otel` is supplied. Instrumentation is off by default.

```bash
dbt build --snowflake-projects-otel
```

Hook spans identify the hook and transaction phase, omit calls that execute no
hooks, and include node context and status.

## Fusion Manifests

After Core loads a Fusion-generated manifest, it reparses adapter macros from
the locally installed `dbt-<adapter>` package. Execution therefore uses macros
from the installed adapter version, not the adapter copy that was present when
Fusion compiled the manifest.

## Python and Dependency Compatibility

The 1.9 line removes Python 3.8 support and requires `dbt-adapters>=1.9.0`.

Core 1.10 adds Python 3.13 support and works with Pydantic v1 or v2. Its patch
releases also:

- Require JSON Schema 4.19.1 or newer.
- Move to Protobuf 6.
- Cap `sqlparse` below 0.5.5.
- Require `dbt-common>=1.37.3`.
- Set the `dbt-adapters` lower bound to 1.16.5 from 1.10.10.
- Temporarily cap `dbt-adapters<1.24` in 1.10.21, then restore `<2.0` in
  1.10.22.

Core 1.11 drops Python 3.9; use Python 3.10 or newer.

Core 1.12 supports Python 3.14 and requires Click 8.3.0,
`dbt-common>=1.37.3`, and `dbt-adapters>=1.24.5`.

## Configurable Parser and Seed Limits

Core 1.12 makes the `MAXIMUM_SEED_SIZE_MIB` limit configurable. Its new
`--sqlparse` option configures SQL-parser limits, avoiding the need to solve
parser limits by pinning a particular `sqlparse` release.
