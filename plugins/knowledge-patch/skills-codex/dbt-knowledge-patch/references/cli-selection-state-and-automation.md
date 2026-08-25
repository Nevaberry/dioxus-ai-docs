# CLI, Selection, State, and Automation

Use this reference for command behavior, selectors, state comparison, parsers, docs serving, and scripts that consume dbt output.

## Machine-readable quiet output (1.9.0)

`dbt show` and `dbt compile` retain their JSON or text result under `--quiet`. Automation can suppress event logs without discarding the command result.

## Test and unit-test selection (1.9.0)

Select unit tests with the `unit_test:` method:

```bash
dbt test --select "unit_test:test_order_total"
```

`dbt test` also accepts `--resource-type` and `--exclude-resource-type`, with corresponding environment-variable flags.

## State selection and deferral (1.9.0)

With `--favor-state`, dbt favors a deferred relation only when its node is not selected by the current command. The `state_modified_compare_more_unrendered_values` behavior flag makes `state:modified` compare additional unrendered database, schema, and source properties while ignoring rendered Jinja in configs.

```yaml
flags:
  state_modified_compare_more_unrendered_values: true
```

For managed functions, `state:modified` detects changes to bodies, configuration, arguments, and return types. With `--defer` and a state manifest, `function()` resolves to the deferred environment's function when it is unselected or has not yet been built in the target.

## Hook-failure selection behavior (1.9.0)

`skip_nodes_if_on_run_start_fails` changes a failed `on-run-start` hook into skipped selected nodes:

```yaml
flags:
  skip_nodes_if_on_run_start_fails: true
```

## Docs-server binding (1.9.0)

`dbt docs serve` accepts `--host` and defaults to `127.0.0.1`. Bind to `0.0.0.0` only when the generated docs must be reachable beyond localhost:

```bash
dbt docs serve --host 0.0.0.0
```

## Exit status (1.9.0)

From Core 1.9.1, a `PartialSuccess` result produces a nonzero exit status. Update CI and wrappers that previously interpreted partial success as a successful process.

## Sample mode (1.10.0)

Sample mode is enabled for `dbt build`. The final interface folds the separate `--sample-window` parameter into `--sample`. Sampling also covers referenced seeds and traverses snapshot dependency graphs.

## Deprecated selection and freshness options (1.10.0)

Use `--select` instead of `--models`, `--model`, or `-m`. Stop using `dbt source freshness --output` or `-o`. The `include` and `exclude` terminology in warn-error options is deprecated as well.

```bash
dbt run --select my_model
```

## Nested JSON output keys (1.11.0)

`dbt ls --output json --output-keys` accepts nested paths:

```bash
dbt ls --output json --output-keys name config.materialized
```

Model records from this command can also contain runtime-only `direct_parents`, identifying the nearest public ancestors. That field is not added to `manifest.json`.

## Named-selector composition (1.12.0)

A selector definition can reference another named selector with the `selector` method:

```yaml
selectors:
  - name: daily
    definition: {method: tag, value: daily}
  - name: daily_alias
    definition: {method: selector, value: daily}
```

## Ad-hoc SQL through run-operation (1.12.0)

`dbt run-operation --sql` executes SQL or Jinja without a wrapper macro. A macro invoked through `run-operation` may call `ref()` on private or protected models.

```bash
dbt run-operation --sql 'select count(*) from {{ ref("orders") }}'
```

## Configurable parser limits (1.12.0)

Use `--sqlparse` to configure SQL-parser limits rather than pinning an older `sqlparse` release. `MAXIMUM_SEED_SIZE_MIB` controls the maximum accepted seed size.

## External V2 parser (1.12.0, updated in 1.12.1)

`--use-v2-parser` bypasses the Core parser, invokes an external parser, and loads the resulting `manifest.json` into the runtime manifest. Select the command with `--v2-parser` or `DBT_ENGINE_V2_PARSER`; the default is `dbt-core-experimental-parser parse`. The command can also be configured under project `flags`.

```bash
dbt parse --use-v2-parser \
  --v2-parser "dbt-core-experimental-parser parse"
```

The initial integration requires `dbt-core-experimental-parser>=2.0.0a4`; the later maintenance requirement raises that minimum to `2.0.0b1`.

## Compilation and status outputs (1.12.0)

`dbt compile` writes compiled snapshot SQL under `target/compiled/`. The Jinja `graph` includes unit tests, and Python-model parsing recognizes `config.meta_get`. `NodeStatus` and `RunStatus` add `Reused`.
