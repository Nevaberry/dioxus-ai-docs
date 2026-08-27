# Coordinate Operation Selection

## Realizations and regional transformations

- EGM2008 grid-transformation records cover WGS 84 realizations (since 9.6.0).
- Operation handling improves between ETRF realizations and between WGS 84
  realizations (since 9.6.0).
- NKG transformations include EUREF-FIN support for Finnish transformations
  (since 9.6.0).
- Transformations between NAD83(CSRS) realizations no longer route through
  NAD83 (since 9.6.1). Reinspect selected pipelines and expected accuracies
  rather than forcing the former intermediate datum.
- Czechia operations from `transformations_czechia.sql` are enabled (since
  9.7.1).
- MTM with CGVD2013 and UTM with CGVD28 are supported for epochs 1997, 2002,
  and 2010 (since 9.8.0).

## Vertical CRS and geoid models

- For a `PROJ {grid_name}` geoid model, `createOperations()` matches the
  vertical datum when selecting an operation (since 9.6.0).
- `getGeoidModels()` uses `vertical_crs.datum_code` to find matching vertical
  CRSs even when their units differ (since 9.6.1).
- Compound-to-compound operations can be created when the two vertical CRS
  definitions are equivalent without being strictly identical (since 9.7.1).
- A vertical transformation can chain through an intermediate same-datum
  vertical CRS (since 9.8.1). For example, EPSG:5705 Baltic 1977 height to
  EPSG:5706 Caspian depth can use the intermediate Baltic 1977 height to
  Caspian height operation.

Do not require literal object equality where PROJ accepts equivalent vertical
CRSs. When an indirect vertical operation is selected, preserve the full chain
in diagnostics and ensure each required resource is available.

## Compound and dimensional operation creation

- Operation creation performs a 2D Helmert transformation when either source or
  target CRS is compound (since 9.6.0).
- Compound-to-geographic construction filters nonsensical transformations
  (since 9.6.1).
- Creation works when both CRSs are compound, one uses `TOWGS84`, and the
  vertical CRSs use different units (since 9.7.0).
- Compound-to-geographic selection applies the vertical transformation from
  “PNG94 / PNGMG94 zone 54 + Kumul 34 height” to “WGS 84 (G2139)” (since
  9.8.0).
- Selection rejects 2D-only transformations when both interpolation source and
  target are 3D CRSs (since 9.8.0).

Compare dimensionality at each interpolation endpoint, not only at the outer
source and target. A pipeline that was previously returned may now be excluded
because it loses a required vertical component.

## National ETRS89 datums

Handling formerly specific to `ETRS89-NOR [EUREF89]` generalizes to other
`ETRS89-XXX` national datums (since 9.8.0). Operation creation and accuracy
calculation improve accordingly, and older EPSG WKT identification is restored
alongside the newer national definitions.

Before depending on this coverage, check the installed database: the bundled
9.8.1 database rolls back the national records added with 9.8.0. Library code
and database content must both support the desired path.

## Time-dependent operations

Epoch values are set in more time-dependent transformation scenarios (since
9.8.1). Provide the intended coordinate epoch and inspect the chosen operation;
do not rely on the former behavior in which an affected transformation could
proceed without its epoch.

Use `projinfo` time-dependence reporting to flag pipelines that need temporal
inputs. Preserve epoch values through application data models rather than
adding an arbitrary default at the final API call.

## Extent and visualization filtering

- Concatenated operations honor `CRS_EXTENT_USE=NONE` (since 9.8.0). Disabling
  CRS-extent use therefore affects their selection as well as simpler
  operations.
- `normalizeForVisualization()` skips extent checks for axis-swap operations
  (since 9.8.0), preventing an extent filter from rejecting a normalization
  step whose purpose is axis order.

Log the option context used during operation discovery. The same source and
target definitions can validly produce different candidate sets under
different extent policies.

## Verification procedure

1. Record source and target WKT or PROJJSON, including dimensionality.
2. Record the PROJ library and database revisions.
3. Check vertical datum identity, equivalence, and units.
4. Supply coordinate epochs for temporal cases.
5. Confirm grids are installed, embedded, or downloadable.
6. Capture the complete selected pipeline and reported accuracy.
7. Repeat in the reverse direction when application behavior requires it.
8. Treat a changed pipeline as potentially intentional until each correction
   above has been excluded.
