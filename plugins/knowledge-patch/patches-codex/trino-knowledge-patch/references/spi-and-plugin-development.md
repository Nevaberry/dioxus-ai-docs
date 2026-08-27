# SPI and plugin development

Use this reference when compiling a connector, event listener, function
plugin, or other extension against a newer Trino SPI. Several migrations are
staged as deprecation followed by removal; target the final API directly.

## Connector lifecycle and context

- Connector-level event listeners are no longer supported, and
  `Connector.getEventListeners()` was removed (469).
- `Connector.getInitialMemoryRequirement()` was removed (471).
- `Connector.shutdown()` no longer has a default implementation; every
  connector must implement it (478).
- `NodeManager.getEnvironment`, `CatalogHandle`, and `@Experimental` were
  removed (477).
- `NodeManager.getCurrentNode` is deprecated; obtain the node from
  `ConnectorContext.getCurrentNode` (477).

## Page sources, sinks, and blocks

### SourcePage migration

`SourcePage` and `ConnectorPageSource.getNextSourcePage()` were introduced in
batch 473-474, with `getNextPage()` deprecated. `getNextPage()` was removed in
477; implementations must now return `SourcePage`.

Deprecated methods were removed from `ConnectorPageSourceProvider`,
`ConnectorPageSinkProvider`, and `TableFunctionProcessorProvider` (482).
Connector page sources receive a `MemoryContext` for reporting memory use
(482).

### Block APIs

- `LazyBlock` was removed (475).
- `getSizeInBytes()` now estimates a block's complete data size (476).
- `RowBlockBuilder` and `ArrayBlockBuilder` have non-callback entry builders
  (479).
- All block types consistently expose raw-array and offset accessors (483).
- Null representation for directly constructed blocks uses bit-packed
  validity bitmaps instead of boolean arrays (483). Code that uses block
  builders does not need a direct-construction migration.

## Type SPI

`Type.appendTo` was deprecated in 478. The deprecated `Type.getObject` and
`Type.appendTo` methods were both removed in 481.

The `Type.getObjectValue` signature no longer takes `ConnectorSession` (477).

The following classes were removed in 480:

- `TypeSignatureParameter`
- `ParameterKind`
- `NamedType`
- `NamedTypeSignature`
- `NamedTypeParameter`

Use `TypeParameter`, including `TypeParameter.Type`,
`TypeParameter.Numeric`, and `TypeParameter.Variable`.

The SPI defines the Iceberg `variant` type (481), supporting experimental
Iceberg v3 variant use.

## Connector metadata

### Columns

The deprecated
`ConnectorMetadata.addColumn(ConnectorSession, ConnectorTableHandle,
ColumnMetadata)` overload was removed (472). Use the overload that also takes
`ColumnPosition`.

`ColumnMetadata.builderFrom` preserves the source column default (479).
`ColumnMetadata.comment` and `ColumnMetadata.extraInfo` use
`Optional<String>` (480).

### Materialized views

`ConnectorMetadata.refreshMaterializedView` was removed (477).
`beginRefreshMaterializedView` and `finishRefreshMaterializedView` no longer
receive handles from other catalogs, and
`delegateMaterializedViewRefreshToConnector` is deprecated.

`MaterializedViewFreshness.getLastFreshTime()` is deprecated; use
`getLastKnownFreshTime()` (480).

### Access control and branches

Table-level `ConnectorAccessControl.checkCanXxx` methods receive a
`tableBranch` parameter (481). Apply authorization to the selected branch,
not only to the base table name.

## Splits, pruning, and pushdown

- `ConnectorSplit.getSplitInfo` was removed (478).
- `ConnectorSplitManager.getSplits` receives dynamic-filter columns rather
  than a `DynamicFilter` (482).
- `ConnectorSplitSource.getNextBatch` receives the current predicate as a
  `DynamicFilterSnapshot` (482).
- `Constraint` no longer contains a predicate. Use
  `ConnectorExpressionEvaluator` for partition and split pruning (482).
- Connector expression pushdown accepts `COALESCE` (481) and lambdas (482).
- Connector table functions can declare descriptions (482).
- Table functions can return large pass-through columns without failing
  (482).

Treat the dynamic-filter migration as one coordinated change: discovery gets
the relevant columns, batch fetching gets a snapshot of the current filter,
and pruning evaluates connector expressions explicitly.

## Scalar function declarations

Java scalar functions can declare method-like invocation syntax (482):

- `@StaticMethod` supports `T::method(args)`.
- `@InstanceMethod` supports `expr.method(args)`.
- `@Name` declares function argument names for `name => value` calls.

These annotations implement the SQL method and named-argument syntax described
in the SQL reference.

## Event-listener SPI

- Connector-level listeners and `Connector.getEventListeners()` were removed
  (469).
- `QueryCompletedEvent` exposes dynamic-filter statistics, and input-table
  metadata includes additional metrics (475).
- `EventListener.splitCompleted` is no longer supported (477).
- `QueryStatistics.totalBytes` and `QueryStatistics.totalRows` were removed
  (477).
- `QueryInputMetadata#connectorMetrics` exposes connector split-source
  metrics (481).
- Event listeners receive query time spent in `FINISHING` (479).

Move server-wide listeners into event-listener plugins rather than returning
them from connectors.

## Upgrade checklist for a plugin

1. Implement `shutdown()` and remove connector-returned event listeners.
2. Move page sources to `SourcePage`; update provider interfaces and memory
   reporting.
3. Replace removed type APIs and type-parameter classes.
4. Update block construction, especially null validity and raw access.
5. Update `addColumn`, column metadata optionals, defaults, and
   materialized-view refresh hooks.
6. Migrate split enumeration, dynamic filters, pruning, and expression
   pushdown together.
7. Add branch-aware authorization if the connector implements table access
   control.
8. Compile and test event-listener consumers against removed statistics and
   callbacks.

