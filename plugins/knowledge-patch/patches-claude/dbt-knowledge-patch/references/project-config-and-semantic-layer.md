# Project Configuration and Semantic Layer

## Column, Source, and Constraint Configuration

The `1.9.0` configuration accepts a `config` mapping on columns. Source
freshness may likewise live under `config`, and explicit null freshness values
are preserved.

```yaml
sources:
  - name: raw
    config:
      freshness:
        warn_after: {count: 12, period: hour}

models:
  - name: orders
    columns:
      - name: id
        config:
          meta:
            owner: analytics
```

Foreign-key constraint expressions can call `ref()` and `source()` rather than
hard-code relation names:

```yaml
models:
  - name: orders
    columns:
      - name: customer_id
        constraints:
          - type: foreign_key
            expression: "{{ ref('customers') }} (id)"
```

## Expanded Resource Metadata

Core 1.10 adds metadata configuration across resource types:

- Saved queries accept `tags`.
- Groups accept `description` and `config.meta`.
- Exposures accept tags and meta config.
- Semantic Layer dimensions, measures, and entities accept meta config.
- Column config meta and tags propagate to tests.
- Offset windows support custom grains.

Core `1.11.0` exposes optional metadata through `config.meta_get(key)` and
required metadata through `config.meta_require(key)` in model Jinja:

```jinja
{{ config(meta={"owner": "finance", "policy": "restricted"}) }}
{% set owner = config.meta_get("owner") %}
{% set policy = config.meta_require("policy") %}
```

## Semantic Layer Additions

Core 1.9 semantic manifests can represent cumulative type parameters, metric
`time_granularity`, and sub-daily granularities. Time-spine YAML accepts new
time-spine settings and uniquely named `custom_granularities`; saved queries
accept `order_by` and `limit`.

Core 1.12 parses new-style V2 Semantic Layer YAML for:

- Standalone and model-attached metrics.
- Entities and derived entities.
- Derived dimensions and `agg_time_dimension`.
- Object-style Semantic Model config and `primary_entity`.

Model-as-Semantic-Model and column-dimension parsing are explicitly not fully
ready in this release.

## OSI Documents

Core 1.12 reads OSI documents from `OSI/` or `osi/` into the manifest. The OSI
directory is configurable, and dbt writes an OSI document after parsing.

## Additional Project Inputs

In `1.12.0`, projects may:

- Declare project variables in `vars.yml`.
- Load environment variables automatically from `.env`.
- Use Jinja-suffixed SQL and Markdown extensions such as `.sql.jinja` and
  `.md.jinja`.

## Catalog Integrations

Core 1.10 parses `catalogs.yml`, including during `parse`, `seed`, and `test`
from 1.10.12 onward. Catalog integration config accepts `file_format`.

Catalog V2 is opt-in in Core 1.12:

```yaml
flags:
  use_catalogs_v2: true
```

Every command that requires a manifest loads catalog configuration. For V1
integrations, `catalog_database` can override the database for any catalog type
and takes highest priority during database-name generation.

## Private Git Packages

Core 1.12 supports private Git packages in both `packages.yml` and
`dependencies.yml`. dbt resolves their URLs from a configured environment
variable when present; otherwise, it constructs an SSH URL.

## Macro and Analysis Configuration

Macro properties accept a `config` mapping containing `meta` and `docs`:

```yaml
macros:
  - name: cents_to_dollars
    config:
      meta: {owner: finance}
      docs: {show: true}
```

Analyses can be enabled or disabled in `dbt_project.yml` at project or folder
scope:

```yaml
analyses:
  my_project:
    staging:
      +enabled: false
```

## Latest-Version Relation Pointers

Versioned models can create an unversioned relation pointer for their latest
version. Enable it project-wide with
`latest_version_pointer_enabled_by_default`, or per model with
`latest_version_pointer`.

Pointer collision checks account for quoting and case. Unquoted floating
versions such as `v: 4.5` are no longer silently dropped.

## Databricks Config Validation

The `1.12.1` batch records that Core 1.12.2 recognizes these Databricks adapter
config keys: `query_tags`, `zorder`, `options`, `unique_tmp_table_suffix`, and
`skip_optimize`. They no longer cause spurious
`CustomKeyInConfigDeprecation` warnings during JSON Schema validation.
