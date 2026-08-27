# Apollo Router Execution, Demand Control, and Delivery

Use this reference for query planning, schema execution, response validation, demand control, error paths, and incremental or WebSocket delivery.

## Query planning and schema execution

### Cooperative query-planning cancellation

Since 2.4.0, `supergraph.query_planning.experimental_cooperative_cancellation` can `measure` a planning timeout or `enforce` it by cancellation. Both `apollo.router.query_planning.plan.duration` and the `query_planning` span carry `outcome`.

### Warm-up compute work is separately observable

Since 2.4.0, parsing/planning cache warm-up after reload runs below live-request priority. Compute duration, queue wait, execution duration, and active-job metrics identify it with `job.type` values `query_parsing_warmup` and `query_planning_warmup`.

### Progressive overrides on interface implementations

Since 2.6.0, the native planner supports labeled `@override` on types and fields implementing interfaces within the same subgraph; these operations no longer fail planning.

### Query planning can enforce a memory ceiling

Since 2.11.0, `experimental_cooperative_cancellation.memory_limit` bounds planning allocation. `enforce` cancels and errors; `measure` records and finishes. It races with `timeout` and requires Unix, `global-allocator`, and no `dhat-heap`.

### Multiple `@listSize` directives

Since 2.12.0, Router processes every `@listSize` on a field and takes the largest `assumedSize`. The behavior remains dormant until Federation composition can emit repeatable directives.

### Deferred query-plan dependencies

Since 2.16.0, plan reduction preserves dependencies supplying entity keys, `__typename`, and other values required by deferred blocks, preventing null or missing deferred fields.

## Demand control

### Per-subgraph demand control

Since 2.12.0, static estimated demand control supports defaults and named-subgraph overrides and sums all fetches to each subgraph. Exceeding one subgraph's limit skips only its calls and composes their values as null while the rest continues.

```yaml
demand_control:
  enabled: true
  mode: enforce
  strategy:
    static_estimated:
      max: 20
      subgraphs:
        all: { max: 8, list_size: 10 }
        subgraphs:
          products: { max: 6 }
```

### Nested and array-based `@listSize` sizing

Since 2.12.0, `@listSize` cost calculation understands array sizing values, nested input paths used to resolve list sizes, and nested field paths in `sizedFields`.

### Actual demand cost includes intermediate work

Since 2.12.0, `demand_control.strategy.static_estimated.actual_cost_mode` defaults to `by_subgraph`, summing all fetch response costs rather than final shape only. Set `response_shape` to restore the prior calculation.

### List arguments can size demand

Since 2.14.0, `@listSize(slicingArguments: [...])` may use a list argument's length as cost multiplier, for inline or variable values.

## Response validation and error paths

### WebSocket handshakes produce valid GraphQL payloads

Since 2.4.0, subscription responses during the handshake satisfy GraphQL validation, including with coprocessors; required `data` is no longer omitted.

### Malformed subgraph errors use concrete array paths

Since 2.5.0, a malformed subgraph value affecting every array element emits one error per concrete index rather than a nonstandard `"@"` segment. Consumers must tolerate more errors and expanded paths.

### Result-coercion errors

Since 2.8.0, misaligned subgraph values are reformatted and nullified. `supergraph.enable_result_coercion_errors: true` additionally sends `RESPONSE_VALIDATION_FAILED` with path and reason, exposing mismatches that were previously silent.

### Unlocatable entity errors target the immediate parent

Since 2.13.0, when an entity error target cannot be determined, Router attaches it to the immediate parent rather than every expected entity, preventing multiplicative fan-out.

### Optional orphan-error hoisting

Since 2.13.0, `experimental_hoist_orphan_errors` can assign incorrect entity paths to the nearest non-array ancestor. Named subgraphs override `all`. It reduces but does not cap error counts.

### Missing fields are result-coercion errors

Since 2.16.0, when result-coercion errors are enabled, a requested field missing from the merged response produces one `RESPONSE_VALIDATION_FAILED` error and one value-completion entry at its source; redundant null-bubble errors are suppressed.
