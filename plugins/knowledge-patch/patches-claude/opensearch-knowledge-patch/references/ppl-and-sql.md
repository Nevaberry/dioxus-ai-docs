# PPL and SQL

Use this reference when generating queries, selecting the Calcite or v2 path, handling pagination and result types, or integrating PPL and SQL tooling.

## Engine routing and execution

### Calcite defaults and fallback

- Calcite becomes the default PPL path in 3.0.0.
- From 3.2.0, a failed Calcite query does not fall back to the v2 engine by default.
- From 3.3.0, a command that Calcite does not support can fall back implicitly to v2. Do not confuse unsupported-command routing with fallback after a general query failure.

### Limits, cancellation, and diagnostics

- Since 3.1.0, `query.size_limit` limits final results only, not intermediate processing.
- In 3.4.0, Calcite queries support timeouts, Explain can emit YAML, and subsearch and join limits are configurable. A zero or negative `subsearch.maxout` means unlimited.
- In 3.5.0, profiling reports phase- and operator-level metrics.
- In 3.6.0, PPL requests accept `fetch_size`, can be cancelled with `_tasks/_cancel`, and expose a grammar-bundle API for third-party tooling.
- In 3.8.0, a configurable expression-depth limit bounds PPL expressions, and `_explain?format=json_tree` returns a machine-readable plan.

### Metadata and data sources

- PPL can reference metadata fields since 2.19.0.
- Direct-query data sources are supported in 3.3.0.
- PIT searches in 3.3.0 use `_shard_doc` as the default sort tiebreaker.

## Relational commands and pipeline shaping

### Initial Calcite command set

The 3.0.0 Calcite path supports `join`, `lookup`, `IN`, relation, `exists`, scalar subqueries, `BETWEEN`, `dedup`, `parse`, multiple index patterns, nested fields, and comments.

### Pipeline expansion

In 3.1.0, Calcite adds:

- `flatten`, `expand`, `trendline`, `appendcol`, and `eventstats`;
- `grok`, `top`, `rare`, `fillnull`, and `describe`;
- `match_only_text` fields and object-field merging during schema discovery.

In 3.3.0, it adds:

- `spath`, `rex`, and `regex`;
- `rex` `sed` mode and `offset_field`;
- `append`, enhanced `join` field lists and options, time modifiers on `search`, wildcard `rename`, and `timechart`.

In 3.4.0, it adds `chart`, `streamstats`, `multisearch`, `replace`, and `appendpipe`.

In 3.5.0, PPL adds `addtotals`, `addcoltotals`, `transpose`, and `mvcombine`; the `ml` command accepts `category_field`.

In 3.6.0, PPL adds:

- bidirectional `graphlookup` with literal starting values;
- `convert`, `mvexpand`, `nomv`, and `fieldformat`;
- result highlighting and `spath` auto-extract;
- the `contains` operator and trailing or empty pipes.

In 3.7.0, PPL adds `union` with type coercion and UNION ALL semantics. Predicates accept `IS NULL` and `IS NOT NULL`; `head` and `top` accept `limit=N`.

In 3.8.0, PPL adds:

- `makeresults` for in-memory rows;
- `foreach` for field lists, multivalue fields, and JSON arrays;
- `timewrap` for period comparisons over `timechart`;
- experimental `xyseries` for pivoting grouped rows to wide tables;
- bare-field join shorthand: `join on <field>`.

## Functions, types, and expressions

### Core functions

The 3.0.0 Calcite path adds JSON casts, `CASE`, `TYPEOF`, and more scalar and data types.

The 3.1.0 function expansion includes:

- `DISTINCT_COUNT_APPROX`, `earliest`, `latest`, and `coalesce`;
- `isempty`, `isblank`, and `ispresent`;
- `geoip`, `cidrmatch`, JSON functions, and cryptographic hashes;
- lambdas, array functions, and decimal literals.

The 3.2.0 Calcite path adds `compare_ip`, IP casts, argument coercion, improved date comparisons, and broader expression support. Date and time functions default to UTC in both PPL and SQL.

### Aggregates and multivalue functions

In 3.3.0:

- `values`, `list`, `first`, and `last` are supported;
- `mvjoin`, `strftime`, and `regex_match` are available;
- `max` and `min` work with nonnumeric values and eval context;
- `distinct_count`, `earliest`, and `latest` work in `eventstats`;
- ISO 8601 strings are accepted.

In 3.4.0:

- eval adds `mvdedup`, `mvindex`, and `mvappend`;
- `timechart` adds per-second, per-minute, per-hour, and per-day functions;
- `replace` supports wildcards, its eval form accepts regex, and `regexp_replace()` is an alias.

In 3.5.0, eval adds `tonumber`, `mvzip`, `split`, `mvfind`, and `mvmap`.

In 3.7.0, `convert` adds `ctime`, `mktime`, `mstime`, `dur2sec`, and a `timeformat` parameter.

### Time and aggregation controls

- In 3.4.0, `streamstats` and `eventstats` support `bucket_nullable`; `top` and `rare` support `usenull`; `timechart` can select `timefield`.
- Span expressions in 3.4.0 support milliseconds, decimal literals, and an implicit `@timestamp`.

### Type and arithmetic behavior

- In 3.3.0, `count(*)` and `dc` cap at `MAX_INTEGER`, and decimal `mod` returns a decimal.
- In 3.4.0, `rex`, `spath`, and `parse` auto-convert extracted types; `geoip` accepts IP-typed input; eval division returns decimal; `like` accepts optional `case_sensitive`.
- In 3.6.0, final struct values are maps rather than lists. Missing or null `JSON_EXTRACT` paths return null, and double overflow to infinity returns null. `FIRST`, `LAST`, and `TAKE` accept text fields and scripts.
- In 3.7.0, `COALESCE(null, integer)` retains integer type. Dotted-path `eval` assignments retain their map root, and `json_set` and `json_delete` handle `$.key` paths.
- In 3.8.0, `constant_keyword` is treated as string, narrow integers widen for arithmetic, and `head` preserves struct and nested columns.

## Command-specific compatibility

### Joins and lookup

- When `plugins.ppl.syntax.legacy.preferred=false`, `join` defaults to `max=1` in 3.5.0.
- `lookup` accepts `OUTPUT` as an alias for `REPLACE` in 3.5.0.
- `spath` supports dynamic fields in 3.5.0.

### Sort, dedup, and wildcard behavior

- An unmatched index pattern raises `IndexNotFoundException` in 3.3.0.
- Calcite `dedup` preserves sort order in 3.7.0.
- A 3.7.0 PPL wildcard search no longer silently drops documents when one index maps a field as text and another as keyword.

## SQL and unified query APIs

### SQL pagination

OpenSearch 3.0.0 removes `plugins.sql.pagination.api`, deprecates Scroll-based pagination, and defaults to Point in Time. Deprecated OpenDistro endpoints and `opendistro`-prefixed settings are removed.

### Unified query APIs

- In 3.6.0, SQL adds a unified query parser, unified-query profiling, and native Calcite SQL planning.
- In 3.7.0, query-only unified V2 blocks DML and DDL. It supports joins, `IN` and `EXISTS` subqueries, derived tables, window functions, `LIMIT`/`OFFSET`, `LENGTH`, `REGEXP_REPLACE`, and `DATE_TRUNC`.
- Also in 3.7.0, SQL adds `vectorSearch()` with k-NN pushdown and filtering modes.
- Under fine-grained access control, SQL cursor continuation remains within the indexes selected by the original query.

### Null predicates

In 3.7.0, `NOT IN` and `NOT LIKE` exclude null and missing values.

## Dashboards query authoring

In 2.19.0, the experimental Discover view adds SQL and PPL beside DQL and Lucene, with autocomplete and improved data selection; experimental features are disabled by default.

In 3.8.0:

- Dashboards adds a visual PPL builder for filters, aggregations, and sorting, with round trips to the raw editor.
- Its lint engine suggests corrections for unknown fields and misspelled commands.
- Dev Tools adds a Grok Debugger that applies a pattern to a sample log and displays extracted fields.
- Discover logs can run SQL with date-picker integration across Logs, Visualization, and Statistics; this is experimental and disabled by default.

## PPL integrations

- In 3.6.0, PPL can create or update Prometheus rules.
- The experimental PPL Alerting assets are removed in 3.6.0 pending refactoring. Dashboards moves to v1 PPL Alerting endpoints and no longer maintains separate legacy and PPL paths.
- In 3.8.0, single-stream anomaly detectors can use PPL as their source and evaluate feature queries through PPL transport actions.
