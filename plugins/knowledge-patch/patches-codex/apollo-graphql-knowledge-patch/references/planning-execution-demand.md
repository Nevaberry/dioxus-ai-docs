# Planning, Execution, Validation, and Demand Control

## Query planning and scheduling

### Cooperative query-planning cancellation (2.4.0)

`supergraph.query_planning.experimental_cooperative_cancellation` can measure or
enforce a planning timeout. `measure` records without cancelling; both the
`apollo.router.query_planning.plan.duration` metric and `query_planning` span
report an `outcome`.

### Query planning can enforce a memory ceiling (2.11.0)

The same configuration accepts
`experimental_cooperative_cancellation.memory_limit`. `enforce` cancels and errors;
`measure` records and completes. Memory and time limits race. Memory enforcement
requires Unix, `global-allocator`, and no `dhat-heap`.

### Warm-up compute work is separately observable (2.4.0)

Post-reload parsing/planning warm-up runs below live-request priority. Compute
duration, queue wait, execution duration, and active-job metrics identify it as
`query_parsing_warmup` or `query_planning_warmup` in `job.type`.

### Native planning rejects unknown execution or security links (2.4.0)

The native planner rejects a supergraph schema containing an unknown `@link`
specification with purpose `EXECUTION` or `SECURITY`. Remove or correct the link.

### Progressive overrides on interface implementations (2.6.0)

The native planner supports labeled `@override` on types and fields that
implement interfaces within the same subgraph; operations that previously
failed planning now execute.

### Deferred query-plan dependencies (2.16.0)

Plan reduction preserves values needed by deferred blocks, including entity
keys and `__typename`, preventing deferred fields from becoming null or absent.

## Input validation and security

### Strict input-object variable validation (2.12.0)

Input-object variables are validated recursively, including rejection of
unknown fields. Set `supergraph.strict_variable_validation: measure` to observe
without enforcing the new behavior.

### Query-validation error redaction (2.12.0)

`supergraph.redact_query_validation_errors: true` replaces all validation
failures with one `invalid query` error carrying `UNKNOWN_ERROR`.

### Multiple `@listSize` directives (2.12.0)

The Router processes every `@listSize` on a field and chooses the greatest
`assumedSize`. In this release the behavior remains dormant until Federation
composition can emit repeatable directives into the supergraph.

### Nested and array-based `@listSize` sizing (2.12.0)

Cost calculation for `@listSize` supports array-style sizing values, nested input paths for
list size, and nested field paths in `sizedFields`.

### List arguments can size demand (2.14.0)

`@listSize(slicingArguments: [...])` can use the length of a list argument as
its multiplier for inline or variable values.

## Demand-control behavior

### Per-subgraph demand control (2.12.0)

Static estimated demand control can set `subgraphs.all` defaults and named
overrides. It sums all fetches to each subgraph across the plan; exceeding a
subgraph limit skips only that subgraph's calls, composes those values as null,
and lets the rest continue.

### Actual demand cost includes intermediate work (2.12.0)

`demand_control.strategy.static_estimated.actual_cost_mode` defaults to
`by_subgraph`, summing response
cost from every fetch rather than only the final response. Set `response_shape`
for the earlier calculation.

## Result coercion and error paths

### Result-coercion errors (2.8.0)

Schema-mismatched subgraph values are reformatted and nullified. With
`supergraph.enable_result_coercion_errors: true`, the client also receives a
`RESPONSE_VALIDATION_FAILED` error containing path and reason.

### Missing fields are result-coercion errors (2.16.0)

When enabled, a requested field missing from the merged result emits one
`RESPONSE_VALIDATION_FAILED` plus one value-completion entry at its source;
redundant null-bubble errors are suppressed.

### Malformed subgraph errors use concrete array paths (2.5.0)

For malformed results affecting every array element, the Router emits one error
per concrete index instead of the nonstandard `"@"` path segment. Consumers
must allow expanded counts and paths.

### Coprocessor execution errors preserve null data (2.2.0)

A coprocessor execution error returned with `data: null` retains that `data`
member in the client response.

### Coprocessor response validation (2.5.0)

The coprocessor-level `response_validation` option controls GraphQL validation
of coprocessor responses and defaults enabled. Subscription termination
responses are validated correctly; disable only deliberately.

### Unlocatable entity errors target the immediate parent (2.13.0)

When an entity error target cannot be determined, the error attaches to the
immediate parent rather than every expected entity, avoiding fan-out.

### Optional orphan-error hoisting (2.13.0)

`experimental_hoist_orphan_errors` assigns incorrect subgraph entity paths to
the nearest non-array ancestor. Named subgraph settings override `all`; this
reduces but does not cap counts.

### GraphQL error selectors are consistently boolean (2.4.0)

Telemetry `on_graphql_error` yields false rather than absent when no error is
present, matches `subgraph_on_graphql_error`, and works at supergraph as well as
router stage.

## Planning and parser observability

### Request allocation histograms (2.11.0)

`apollo.router.request.memory` covers full-request allocation and
`apollo.router.query_planner.memory` covers planning compute jobs, with
`allocation.type` and `context`. Availability matches planning memory limits:
Unix, `global-allocator`, and no `dhat-heap`.

### Parser-complexity metrics (2.12.0)

`apollo.router.operations.recursion` records parser recursion depth and
`apollo.router.operations.lexical_tokens` records query token count.
