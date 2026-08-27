# Coordinate-Operation Selection

## Datum Realizations and Regional Operations

- Operation handling improves between ETRF realizations and between WGS 84
  realizations (since 9.6.0).
- NKG transformations include EUREF-FIN support for Finnish transformations
  (since 9.6.0).
- Transformations between NAD83(CSRS) realizations no longer route through
  NAD83 (since 9.6.1). The selected pipeline can therefore change.
- Czechia-specific transformations from `transformations_czechia.sql` are
  available for discovery and use (since 9.7.1).
- Handling once special-cased for `ETRS89-NOR [EUREF89]` applies to other
  `ETRS89-XXX` national datums (since 9.8.0). Operation creation and accuracy
  calculation improve along with this generalization.

Authority-data rollback in 9.8.1 removes the national-realization records added
by EPSG 12.049 even though the generalized factory behavior remains relevant.
Always distinguish factory logic from record availability.

## Vertical Datum and Geoid Selection

- For a `PROJ {grid_name}` geoid model, `createOperations()` selects an
  operation by matching the vertical datum (since 9.6.0).
- `getGeoidModels()` uses `vertical_crs.datum_code` when locating vertical
  CRSs (since 9.6.1), allowing it to find matching definitions with different
  units.
- Equivalent but not strictly identical vertical CRSs can participate in
  compound-to-compound operations (since 9.7.1).
- A vertical transformation can chain through an intermediate same-datum
  vertical CRS (since 9.8.1). For example, EPSG:5705 (Baltic 1977 height) to
  EPSG:5706 (Caspian depth) can use the intermediate Baltic 1977 height to
  Caspian height operation.

When no direct operation appears, inspect datum equivalence, units, available
grid models, and viable intermediate vertical CRSs.

## Compound and Three-Dimensional CRSs

- `createOperations()` performs a 2D Helmert transformation when either source
  or target CRS is compound (since 9.6.0).
- Compound-to-geographic construction filters out nonsensical transformations
  (since 9.6.1).
- When both CRSs are compound, operation creation handles one CRS using
  `TOWGS84` while the vertical CRSs use different units (since 9.7.0).
- Compound-to-geographic selection applies the vertical transformation from
  “PNG94 / PNGMG94 zone 54 + Kumul 34 height” to “WGS 84 (G2139)” (since
  9.8.0).
- Operation creation rejects 2D-only transformations when both interpolation
  source and target are 3D CRSs (since 9.8.0).

Dimension filtering is a correctness constraint. Do not reintroduce a rejected
2D candidate merely to obtain a pipeline.

## Epoch Handling

Epoch values are set in more time-dependent transformation scenarios (since
9.8.1). Pipelines that previously ran without the intended epoch can now
produce different coordinates.

For dynamic CRSs:

1. Preserve coordinate metadata through every application layer.
2. Inspect the generated operation for time-dependent steps.
3. Supply the intended epoch rather than relying on an implicit default.
4. Compare both pipeline construction and execution when upgrading.

## Extent and Visualization Filtering

- Concatenated operations honor `CRS_EXTENT_USE=NONE` (since 9.8.0). Disabling
  CRS-extent use now affects their selection as well as simpler operations.
- `normalizeForVisualization()` skips extent checks for axis-swap operations
  (since 9.8.0), preventing extent filtering from rejecting normalization
  steps.

An axis swap changes representation rather than geographic validity. Keep it
separate from geographic area-of-use filtering when diagnosing a missing
visualization-normalized operation.

## Supported Operation Methods

Since 9.6.0:

- EPSG “Vertical Offset by Grid Interpolation (asc)” maps to
  `+proj=vgridshift`.
- Full-matrix coordinate-frame rotation methods are recognized for geocentric
  and geographic-2D coordinates.
- JSON TIN interpolation methods are recognized for Cartesian-grid and vertical
  offsets.

The ellipsoidal Equidistant Cylindrical operation method EPSG:1028 is supported
since 9.8.0.

## Selection Review Checklist

For each unexpected candidate or pipeline, compare:

- source and target CRS components and dimensionality;
- datum realization and vertical datum;
- coordinate epoch for dynamic transformations;
- interpolation CRS dimensionality;
- vertical units and semantic equivalence;
- area of interest and `CRS_EXTENT_USE`;
- installed grid files and database alternatives;
- operation accuracy and intermediate steps; and
- authority-database revision.
