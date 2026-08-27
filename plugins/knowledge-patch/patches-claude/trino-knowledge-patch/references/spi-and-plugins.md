# SPI and Plugin Development

Use this reference when compiling or migrating connectors, event listeners,
functions, table functions, and block-processing code.

## Removed and replaced connector APIs

- Connector-scoped event listeners and `Connector.getEventListeners()` were
  removed (469). `Connector.getInitialMemoryRequirement()` was removed (471).
- The old three-argument `ConnectorMetadata.addColumn(session, table, column)`
  overload was removed; pass `ColumnPosition` (472).
- Migrate page sources to `SourcePage` and
  `ConnectorPageSource.getNextSourcePage()`, introduced in 473-474. The old
  `getNextPage()` was removed in 477.
- `ConnectorMetadata.refreshMaterializedView` was removed;
  `beginRefreshMaterializedView` and `finishRefreshMaterializedView` no longer
  receive handles from other catalogs; and
  `delegateMaterializedViewRefreshToConnector` is deprecated (477).
- `Connector.shutdown()` no longer has a default implementation (478), and
  `ConnectorSplit.getSplitInfo()` was removed (478).
- Table-level `ConnectorAccessControl.checkCanXxx` methods take a `tableBranch`
  parameter (481).
- Deprecated methods were removed from `ConnectorPageSourceProvider`,
  `ConnectorPageSinkProvider`, and `TableFunctionProcessorProvider` (482).

## Event, node, and metadata SPI

- `EventListener.splitCompleted` and `QueryStatistics.totalBytes`/`totalRows`
  were removed (477).
- `QueryCompletedEvent` exposes dynamic-filter statistics and richer input-table
  metrics (475); `QueryInputMetadata#connectorMetrics` exposes split-source
  metrics (481).
- `Type.getObjectValue` no longer takes `ConnectorSession`.
  `NodeManager.getEnvironment`, `CatalogHandle`, and `@Experimental` were
  removed; replace deprecated `NodeManager.getCurrentNode` with
  `ConnectorContext.getCurrentNode` (477).
- `MaterializedViewFreshness.getLastFreshTime()` is deprecated; use
  `getLastKnownFreshTime()` (480).
- `ColumnMetadata.comment` and `.extraInfo` are `Optional<String>` (480), and
  `ColumnMetadata.builderFrom` preserves a default value (479).

## Types, blocks, and memory

- `LazyBlock` was removed (475).
- `getSizeInBytes()` now estimates a block's complete data size (476).
- Non-callback entry builders are available on `RowBlockBuilder` and
  `ArrayBlockBuilder` (479).
- `TypeSignatureParameter`, `ParameterKind`, `NamedType`, `NamedTypeSignature`,
  and `NamedTypeParameter` were removed. Use `TypeParameter` and its `Type`,
  `Numeric`, and `Variable` variants (480).
- `Type.appendTo` was deprecated in 478; both `Type.getObject` and
  `Type.appendTo` were removed in 481.
- All block implementations expose raw-array and offset access consistently
  (483). Nulls are represented by bit-packed validity maps, not boolean arrays;
  direct block constructors must migrate, while builder-based code is unaffected
  (483).
- Connector page sources receive a `MemoryContext` for reporting memory use
  (482).

## Expressions, functions, pruning, and table functions

- Connector expression pushdown supports `COALESCE` (481) and lambdas (482).
- Java scalar functions can use `@StaticMethod` for `T::method(args)`,
  `@InstanceMethod` for `expr.method(args)`, and `@Name` for argument names
  (482).
- Connector table functions can declare descriptions (482).
- `ConnectorSplitManager.getSplits` now receives dynamic-filter columns rather
  than a `DynamicFilter`. `ConnectorSplitSource.getNextBatch` receives a
  `DynamicFilterSnapshot`; `Constraint` no longer carries a predicate; use
  `ConnectorExpressionEvaluator` for partition/split pruning (482).
