# Managed Functions

## Function Resources

The `1.11-udfs` batch lets dbt manage warehouse functions as DAG resources.
Put a body in `functions/<name>.sql` or `functions/<name>.py`, and define its
required name and return type, arguments, and optional config in a corresponding
properties file. dbt combines these inputs into `CREATE FUNCTION` and creates,
updates, or renames the function before dependent models.

```sql
-- functions/is_positive_int.sql (Snowflake expression body)
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

## SQL Functions

SQL functions are supported on BigQuery, Snowflake, Redshift, Postgres, and
Databricks. Adapter body conventions differ:

- BigQuery, Snowflake, and Databricks use expression bodies.
- Redshift and Postgres bodies use a `SELECT`.
- Argument defaults are available only on Snowflake and Postgres.
- BigQuery ignores `volatility` for both SQL and Python functions and emits a
  warning; Snowflake applies it.

## Python Functions

Python function resources work on Snowflake, BigQuery, and Databricks with
Unity Catalog. Snowflake and BigQuery require `runtime_version` and
`entry_point`, and can install optionally version-pinned warehouse packages.
Snowflake supports Python 3.10 through 3.13; BigQuery supports Python 3.11.

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

Databricks accepts `runtime_version` and `entry_point` for cross-adapter
compatibility but warns that they have no effect. It embeds the `.py` file
verbatim as the function body, so the file needs a top-level return rather
than the shape of a standalone Python module:

```python
import re
def main(a_string):
    return 1 if re.search(r'^[0-9]+$', a_string or '') else 0
return main(a_string)
```

## JavaScript Functions

Core 1.12 adds `.js` bodies on Snowflake and BigQuery. JavaScript on another
adapter is a parse error.

```javascript
// functions/is_positive_int.js
return /^[0-9]+$/.test(a_string) ? 1 : 0;
```

Snowflake can quote argument names with `config.snowflake.quote_args`:

```yaml
config:
  snowflake:
    quote_args: true
```

BigQuery applies `deterministic` and `non-deterministic` volatility but does
not support `stable`.

## Overloads

Core 1.12 adds the `overloads` property, giving one function name multiple
argument signatures. Each overload identifies a separate body through
`defined_in` and may override `arguments` and `returns`. If `returns` is
omitted, the root return type is inherited.

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

SQL overloads work on Snowflake and Postgres. Python and JavaScript overloads
work on Snowflake. All signatures share one DAG node and are built and selected
together. `dbt retry` reruns only the overloads that failed.

## References and Selection

Use `function()` rather than hard-coding the qualified warehouse name. It
compiles to the qualified function and records a function-to-model DAG edge.

```sql
select {{ function('is_positive_int') }}(value) as is_positive
from {{ ref('input_values') }}
```

```bash
dbt list --select "resource_type:function"
dbt build --select "resource_type:function"
dbt build --select is_positive_int
```

Body, config, argument, and return-type changes all participate in
`state:modified`.

With `--defer` and a state manifest, `function()` resolves to the deferred
environment's existing function when the function is not selected or has not
yet been built in the target environment.

## Unit Tests and Limits

Unit tests do not implicitly create the warehouse function. Build it and the
tested model's ancestors before running the unit test:

```bash
dbt build --select "+my_model_to_test" --empty
```

Only scalar and aggregate functions are supported. Java, Scala, and other UDF
languages are not supported.
