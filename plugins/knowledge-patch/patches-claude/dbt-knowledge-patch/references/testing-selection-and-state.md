# Testing, Selection, and State

## Unit-Test Selection and Configuration

The `1.9.0` behavior adds the `unit_test:` selection method:

```bash
dbt test --select "unit_test:test_order_total"
```

`dbt test` accepts `--resource-type` and `--exclude-resource-type`, together
with corresponding environment-variable flags. Unit tests may be disabled by
config and may use versioned refs.

The older `tests:` property remains accepted alongside `data_tests:` without a
deprecation warning.

## Data-Test Configuration

Data tests accept arbitrary config options. Adapters receive them through
their `pre_model` and `post_model` hooks.

Generic-test arguments move beneath `arguments` when
`require_generic_test_arguments_property` is enabled. That flag appears in
Core 1.10.5 with a `false` default and defaults to `true` in 1.10.8.

```yaml
models:
  - name: orders
    columns:
      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: [placed, shipped, completed]
```

Core `1.12.0` provides two additional test opt-ins:

```yaml
flags:
  require_sql_header_in_test_configs: true
  support_custom_ref_kwargs: true
```

`require_sql_header_in_test_configs` lets data tests use `sql_header`.
`support_custom_ref_kwargs` lets unit tests and generic data tests pass custom
keyword arguments to `ref()`.

## State Deferral and Comparison

With `--favor-state`, a deferred relation is favored only when its node is not
selected in the current command.

`state_modified_compare_more_unrendered_values` expands `state:modified`
comparison to additional unrendered database, schema, and source properties,
while ignoring rendered Jinja in configs.

```yaml
flags:
  state_modified_compare_more_unrendered_values: true
```

For managed functions, changes to the body, config, arguments, or return type
are all detected by `state:modified`. With `--defer`, `function()` uses the
deferred environment's function if it is unselected or not yet built locally.

## Hook Failure Behavior

`skip_nodes_if_on_run_start_fails` changes a failed `on-run-start` hook into
skipped selected nodes:

```yaml
flags:
  skip_nodes_if_on_run_start_fails: true
```

## Resource and Package Name Resolution

The `1.11.0` behavior adds:

- `require_unique_project_resource_names`, which restores an error for
  duplicate node names inside one project.
- `require_ref_searches_node_package_before_root`, which makes an ambiguous
  package-internal `ref()` search the referencing node's package before the
  root project.

## Named-Selector Composition

A Core 1.12 selector definition can reference another named selector through
the `selector` method:

```yaml
selectors:
  - name: daily
    definition: {method: tag, value: daily}
  - name: daily_alias
    definition: {method: selector, value: daily}
```

## Managed Function Selection and Tests

Select function resources by resource type or name:

```bash
dbt list --select "resource_type:function"
dbt build --select "resource_type:function"
dbt build --select is_positive_int
```

Unit tests do not create a referenced warehouse function implicitly. Build the
function and tested model's ancestors first:

```bash
dbt build --select "+my_model_to_test" --empty
```

All overloads share one DAG node and are selected and built together. A retry
reruns only overloads that failed.
