# PPL, SQL, Query APIs, and Transports

## Routing and executing PPL

### Calcite selection and fallback

Calcite is enabled by default for PPL in 3.0.0. Since 3.2.0, failed Calcite queries do not fall back to the v2 engine by default. OpenSearch 3.3.0 refines this: unsupported commands implicitly route to v2, but general query failures still do not.

PPL supports direct-query data sources in 3.3.0. Point-in-Time searches use `_shard_doc` as the default sort tiebreaker.

Since 3.4.0, Calcite queries accept timeouts, Explain can return YAML, and subsearch and join limits are configurable. A zero or negative `subsearch.maxout` means unlimited.

When `plugins.ppl.syntax.legacy.preferred=false`, `join` defaults to `max=1` in 3.5.0. Profiling can report phase- and operator-level metrics.

In 3.6.0, PPL requests accept `fetch_size`, can be cancelled through `_tasks/_cancel`, and expose a grammar-bundle API for third-party query tooling.

## Composing PPL pipelines

### Relational and shaping commands

The 3.0.0 Calcite path supports `join`, `lookup`, `IN`, relation, `exists`, scalar subqueries, `BETWEEN`, `dedup`, `parse`, multiple index patterns, nested fields, and comments.

OpenSearch 3.1.0 adds `flatten`, `expand`, `trendline`, `appendcol`, `grok`, `top`, `rare`, `fillnull`, `describe`, and `eventstats`. It supports `match_only_text` and merges object fields while discovering an index schema.

OpenSearch 3.3.0 adds `spath`, `rex`, `regex`, and `append`. `rex` supports `sed` mode and `offset_field`; `join` gains field lists and options, `search` gains time modifiers, `rename` accepts wildcards, and Calcite supports `timechart`.

In 3.4.0, Calcite adds `chart`, `streamstats`, `multisearch`, `replace`, and `appendpipe`. `replace` supports wildcards, its eval form supports regex, and `regexp_replace()` is an alias. `timechart` adds per-second, per-minute, per-hour, and per-day functions.

Since 3.5.0, PPL includes `addtotals`, `addcoltotals`, `transpose`, and `mvcombine`; `lookup` accepts `OUTPUT` as an alias for `REPLACE`, and `spath` supports dynamic fields. The `ml` command accepts `category_field`.

OpenSearch 3.6.0 adds bidirectional `graphlookup` with literal starting values, `convert` with five conversion functions, `mvexpand`, `nomv`, and `fieldformat`. It adds highlighting, automatic extraction for `spath`, a `contains` operator, and trailing or empty pipes.

In 3.7.0, `union` applies type coercion and UNION ALL semantics. Predicates accept `IS [NOT] NULL`, while `head` and `top` accept `limit=N`.

OpenSearch 3.8.0 adds `makeresults`, `foreach` over field lists, multivalue fields, and JSON arrays, `timewrap` for period comparison over `timechart`, and experimental `xyseries` for pivoting grouped rows to wide output. Bare-field join shorthand uses `join on <field>`.

### Aggregation and window controls

In 3.4.0, `streamstats` and `eventstats` accept `bucket_nullable`; `top` and `rare` accept `usenull`; `timechart` chooses its timestamp through `timefield`. Span expressions accept milliseconds, decimal literals, and an implicit `@timestamp`.

Since 3.3.0, `values` and `list` statistics, `first` and `last` aggregates, and `distinct_count`, `earliest`, and `latest` in `eventstats` are supported. `count(*)` and `dc` cap at `MAX_INTEGER`.

## Writing PPL expressions

### Scalar, JSON, and collection functions

OpenSearch 3.0.0 adds JSON casts, `CASE`, `TYPEOF`, and additional scalar and data types.

OpenSearch 3.1.0 adds `DISTINCT_COUNT_APPROX`, `earliest`, `latest`, `coalesce`, `isempty`, `isblank`, `ispresent`, `geoip`, `cidrmatch`, JSON functions, cryptographic hashes, lambdas, array functions, and decimal literals.

OpenSearch 3.3.0 adds `mvjoin`, `strftime`, `regex_match`, nonnumeric and eval-context `max` and `min`, and ISO 8601 strings. Decimal `mod` returns a decimal.

In 3.4.0, multivalue eval adds `mvdedup`, `mvindex`, and `mvappend`. `rex`, `spath`, and `parse` extractions automatically convert types; `geoip` accepts IP-typed input; eval division returns a decimal; and `like` accepts optional `case_sensitive`.

OpenSearch 3.5.0 adds `tonumber`, `mvzip`, `split`, `mvfind`, and `mvmap`.

In 3.7.0, `convert` adds `ctime`, `mktime`, `mstime`, `dur2sec`, and `timeformat`.

### Result and null behavior

Since 3.1.0, `query.size_limit` limits only final results, not intermediate processing.

In 3.2.0, Calcite adds `compare_ip`, IP casts, argument coercion, improved date comparisons, and broader expression support. Date and time functions default to UTC across PPL and SQL.

In 3.3.0, unmatched index patterns raise `IndexNotFoundException`.

OpenSearch 3.6.0 returns final struct values as maps rather than lists. Missing or null `JSON_EXTRACT` paths return null, and arithmetic that overflows a double to infinity returns null. `FIRST`, `LAST`, and `TAKE` accept text fields and scripts.

OpenSearch 3.7.0 makes `NOT IN` and `NOT LIKE` exclude null or missing values. `COALESCE(null, integer)` preserves integer type; wildcard searches no longer silently discard documents when a field is text in one index and keyword in another; `dedup` preserves sort order; dotted-path `eval` assignments preserve the root map; and `json_set` and `json_delete` handle `$.key` paths.

Since 3.8.0, `constant_keyword` is treated as a string, narrow integers widen for arithmetic, and `head` retains struct and nested columns. A configurable expression-depth limit constrains complex expressions, and `_explain?format=json_tree` returns machine-readable plans.

## Using PPL metadata and authoring tools

PPL queries can reference metadata fields since 2.19.0.

OpenSearch Dashboards 3.8.0 adds a visual PPL builder for filters, aggregations, and sorting with round-trip editing, plus lint suggestions for unknown fields and misspelled commands. Dev Tools adds a Grok Debugger that simulates a pattern against a sample log and displays extracted fields.

## Using SQL and unified query APIs

### SQL lifecycle

OpenSearch 3.0.0 removes the SparkSQL connector and SQL `DELETE`, deprecates the OpenSearch DSL format and several settings, removes `plugins.sql.pagination.api`, and defaults pagination to Point in Time. Scroll-based pagination is deprecated, and OpenDistro endpoints and `opendistro`-prefixed settings are removed.

OpenSearch 3.6.0 adds a unified query parser API, profiling for the unified API, and native Calcite SQL planning.

In 3.7.0, SQL adds `vectorSearch()` with k-NN pushdown and filtering modes. The query-only unified V2 path blocks DML and DDL and supports joins, `IN` and `EXISTS` subqueries, derived tables, window functions, `LIMIT`/`OFFSET`, `LENGTH`, `REGEXP_REPLACE`, and `DATE_TRUNC`.

SQL cursor continuation in 3.7.0 remains within the original query indexes under fine-grained access control.

## Operating PPL Alerting

PPL Alerting 3.4.0 adds monitor execute and statistics plus get, search, and delete monitor operations and alert retrieval/lifecycle operations. Alerting V2 roles are added to `roles.yml`, and Dashboards bucket-level triggers can carry keyword filters.

OpenSearch 3.6.0 removes the experimental PPL Alerting assets pending refactoring. Dashboards APIs move to v1 endpoints and no longer maintain separate legacy and PPL paths. PPL can create or update Prometheus rules.

In 3.7.0, Alerting provides PPL monitor CRUD and manual execution with RBAC checks. PPL monitor names can contain up to 100 characters rather than 30.

## Choosing ingestion and wire transports

### Protobuf over gRPC

OpenSearch 3.0.0 introduces disabled-by-default Protobuf-over-gRPC transport and experimental bulk ingestion. OpenSearch 3.2.0 makes the transport production-ready for bulk ingestion, expands search coverage including k-NN, and adds encryption in transit.

OpenSearch 3.3.0 expands gRPC to term-level, full-text, geographic, Boolean, script, and nested queries and publishes OpenSearch protobuf Python packages to PyPI.

In 3.4.0, gRPC search adds `ConstantScoreQuery`, `FuzzyQuery`, `MatchBoolPrefixQuery`, `MatchPhrasePrefix`, `PrefixQuery`, and `MatchQuery`; bulk documents can be CBOR, SMILE, or YAML.

OpenSearch 3.5.0 adds circuit-breaker protection, Security JWT authentication, case-insensitive JWT header names, and hybrid queries over gRPC. OpenSearch 3.6.0 adds Security Basic authentication.

### Apache Arrow Flight

OpenSearch 3.3.0 adds a separate disabled-by-default Apache Arrow Flight transport for secured server-side node-to-node streaming through `StreamTransportService`.

### HTTP/3 and pull-based ingestion

OpenSearch 3.5.0 adds disabled-by-default server-side HTTP/3.

Pull-based ingestion from Apache Kafka and Amazon Kinesis begins as a disabled-by-default 3.0.0 experiment with native backpressure. It becomes generally available in 3.6.0 with warmup settings and adaptive shard selection.
