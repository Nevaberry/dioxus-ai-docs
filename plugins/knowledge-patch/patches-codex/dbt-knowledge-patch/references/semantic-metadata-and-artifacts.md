# Semantic Metadata and Artifacts

Use this reference for Semantic Layer and OSI parsing, metadata configuration, manifest and log fields, artifact uploads, and telemetry.

## Semantic Layer schema additions (1.9.0)

Semantic manifests can represent cumulative type parameters, metric `time_granularity`, and sub-daily granularities. Time-spine YAML accepts new time-spine settings and uniquely named `custom_granularities`. Saved queries accept `order_by` and `limit`.

## Expanded resource metadata (1.10.0)

Saved queries accept `tags`. Groups accept `description` and `config.meta`; exposures accept tags and meta config. Semantic Layer dimensions, measures, and entities accept meta config. Column meta and tags propagate to tests, and offset windows support custom grains.

## Artifact, log, lock-file, and upload fields (1.10.0)

Artifact metadata includes an invocation-start timestamp and quoting configuration. Manifest nodes and columns include `doc_blocks`. Structured-log `node_info` includes `node_checksum`, and package lock entries include `name`. Core can also upload artifacts to dbt Cloud.

Consumers should tolerate additive fields and distinguish manifest data from command-only output.

## V2 Semantic Layer YAML (1.12.0)

Core parses new-style V2 Semantic Layer YAML for:

- standalone and model-attached metrics;
- entities and derived entities;
- derived dimensions;
- `agg_time_dimension`;
- object-style Semantic Model config; and
- `primary_entity`.

Model-as-Semantic-Model and column-dimension parsing are explicitly not fully ready in this release. Validate the emitted manifest before making downstream tooling depend on those shapes.

## OSI documents (1.12.0)

Core reads OSI documents from `OSI/` or `osi/` into the manifest. Their directory is configurable, and an OSI document is written after parsing. Treat the configured directory and generated document as part of parse-time inputs and outputs.

## Compilation and tooling outputs (1.12.0)

`dbt compile` writes compiled snapshot SQL under `target/compiled/`. The Jinja `graph` includes unit tests. `NodeStatus` and `RunStatus` include `Reused`.

Model rows from `dbt ls --output json` include runtime-only `direct_parents`, containing nearest public ancestors. This field does not alter `manifest.json`.

## OpenTelemetry node and hook spans (1.12.1)

Core 1.12.1 can emit OpenTelemetry spans for node and hook execution when `--snowflake-projects-otel` is supplied. Instrumentation is off by default.

```bash
dbt build --snowflake-projects-otel
```

Hook spans identify the hook and transaction phase, include node context and status, and are omitted when a call executes no hooks.

## Deprecated-version warnings (1.12.1)

Core 1.12.2 warns when the installed dbt version is deprecated. Do not suppress this as an ordinary project-schema diagnostic; use it to schedule a runtime upgrade.
