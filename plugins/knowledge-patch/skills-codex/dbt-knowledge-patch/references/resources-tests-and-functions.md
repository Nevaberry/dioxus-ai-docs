# Resources, Tests, Snapshots, and Functions

Use this reference for managed warehouse functions, tests, constraints, versioned models, macro metadata, analyses, and resource-name behavior.

## Unit and data-test configuration (1.9.0)

Data tests accept arbitrary config options, which are passed to adapter `pre_model` and `post_model` hooks. Unit tests may be disabled through config and may use versioned refs. The older `tests:` key remains accepted without a deprecation warning alongside `data_tests:`.

Columns may carry `config`; column meta and tags propagate to tests.

## Foreign-key constraint references (1.9.0)

Foreign-key constraint expressions may use `ref()` and `source()` instead of hard-coded relation names:

```yaml
models:
  - name: orders
    columns:
      - name: customer_id
        constraints:
          - type: foreign_key
            expression: "{{ ref('customers') }} (id)"
```

## Managed UDF resource layout (1.11-udfs)

Managed functions are DAG resources. Put the body in `functions/<name>.sql` or `functions/<name>.py`, then define the required name and return type, arguments, and optional config in a properties file. dbt combines these into `CREATE FUNCTION` and creates, updates, or renames the function before dependent models.

```sql
-- functions/is_positive_int.sql, Snowflake expression body
REGEXP_INSTR(a_string, '^[0-9]+$')
```

```yaml
functions:
  - name: is_positive_int
    config:
      schema: udf_schema
      volatility: deterministic
    arguments:
      - name: a_string
        data_type: string
    returns:
      data_type: integer
```

SQL functions work on BigQuery, Snowflake, Redshift, Postgres, and Databricks. BigQuery, Snowflake, and Databricks use expression bodies; Redshift and Postgres require a `SELECT` body. Argument defaults are available only on Snowflake and Postgres. BigQuery warns and ignores `volatility` for SQL and Python functions, while Snowflake applies it.

Only scalar and aggregate functions are supported. Java, Scala, and other function languages are not supported.

## Python UDFs (1.11-udfs)

Python function resources work on Snowflake, BigQuery, and Databricks with Unity Catalog. Snowflake and BigQuery require `runtime_version` and `entry_point`; they can install warehouse packages with optional version pins. Snowflake supports Python 3.10–3.13 and BigQuery supports Python 3.11.

```yaml
functions:
  - name: is_positive_int
    config:
      runtime_version: "3.11"
      entry_point: main
      packages: [numpy, "pandas==1.5.0"]
    arguments:
      - {name: a_string, data_type: string}
    returns: {data_type: integer}
```

Databricks accepts `runtime_version` and `entry_point` only for cross-adapter compatibility and warns that they have no effect. It embeds the `.py` file verbatim as the body, so the file needs a top-level return rather than the shape of a standalone module:

```python
import re
def main(a_string):
    return 1 if re.search(r'^[0-9]+$', a_string or '') else 0
return main(a_string)
```

## JavaScript UDFs (1.11-udfs)

Core 1.12 accepts `.js` bodies on Snowflake and BigQuery. JavaScript on another adapter is a parse error. Snowflake can quote argument names with `config.snowflake.quote_args`; BigQuery applies `deterministic` and `non-deterministic` volatility but does not support `stable`.

```javascript
return /^[0-9]+$/.test(a_string) ? 1 : 0;
```

```yaml
config:
  snowflake:
    quote_args: true
```

## Overloaded UDFs (1.11-udfs)

`overloads` gives one function name multiple argument signatures. Each overload names a distinct body with `defined_in` and may replace `arguments` and `returns`; an omitted return type inherits the root return type.

```yaml
functions:
  - name: is_positive_int
    arguments:
      - {name: a_string, data_type: string}
    returns: {data_type: integer}
    overloads:
      - defined_in: is_positive_int_numeric
        arguments:
          - {name: a_num, data_type: numeric}
```

SQL overloads work on Snowflake and Postgres. Python and JavaScript overloads work on Snowflake. All signatures share one DAG node and are built and selected together; `dbt retry` reruns only the overloads that failed.

## Function references, selection, and state (1.11-udfs)

Call `function()` instead of hard-coding a qualified warehouse name. dbt compiles the qualified name and records a function-to-model DAG edge:

```sql
select {{ function('is_positive_int') }}(value) as is_positive
from {{ ref('input_values') }}
```

```bash
dbt list --select "resource_type:function"
dbt build --select "resource_type:function"
dbt build --select is_positive_int
```

Body, config, argument, and return-type changes are detected by `state:modified`. With `--defer` and a state manifest, `function()` uses the deferred environment's existing function when it is not selected or has not yet been built in the target.

## Unit tests with functions (1.11-udfs)

Unit tests do not create a warehouse function implicitly. Build it and the tested model's ancestors first:

```bash
dbt build --select "+my_model_to_test" --empty
```

## Metadata accessors in model Jinja (1.11.0)

Use `config.meta_get(key)` for optional metadata and `config.meta_require(key)` for required metadata:

```jinja
{{ config(meta={"owner": "finance", "policy": "restricted"}) }}
{% set owner = config.meta_get("owner") %}
{% set policy = config.meta_require("policy") %}
```

## Latest-version relation pointers (1.12.0)

Versioned models can create an unversioned relation pointer, such as `dim_customers`, for the latest version. Enable pointers project-wide with `latest_version_pointer_enabled_by_default` or per model with `latest_version_pointer`.

```yaml
flags:
  latest_version_pointer_enabled_by_default: true
```

Collision checks honor quoting and case. Unquoted floating versions such as `v: 4.5` are no longer silently discarded.

## Test ref and SQL-header opt-ins (1.12.0)

Data tests may use `sql_header` behind `require_sql_header_in_test_configs`. Unit tests and generic data tests may pass custom `ref()` keyword arguments behind `support_custom_ref_kwargs`.

## Macro and analysis configuration (1.12.0)

Macro properties accept `config.meta` and `config.docs`. Analyses may be enabled or disabled from `dbt_project.yml` at project or folder scope. Python-model parsing recognizes `config.meta_get`, and the Jinja `graph` includes unit tests.
