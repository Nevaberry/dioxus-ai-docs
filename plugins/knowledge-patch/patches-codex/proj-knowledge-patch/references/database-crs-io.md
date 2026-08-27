# Database, CRS Identification, and Serialization

## Authority Database Revisions

Database content changes independently from API behavior. Match identifiers and
expected operations to the database shipped by the installed patch release:

- 9.6.0 uses EPSG 12.004. It adds `engineering_datum` and `engineering_crs`
  tables with related EPSG records, ingests deprecated ESRI names for older
  ESRI WKT, and adds the optional `step_direction` column to
  `concatenated_operation_step`.
- 9.6.1 uses EPSG 12.012 and ESRI definitions from ArcGIS Pro 3.5.
- 9.6.2 uses EPSG 12.013.
- 9.7.0 uses EPSG 12.022 and restores legacy `alias_name` values removed from
  newer EPSG data, improving recognition of older WKT names.
- 9.7.1 uses EPSG 12.029.
- 9.8.0 uses EPSG 12.049 and ArcGIS Pro 3.6 ESRI records. It creates ESRI
  aliases for geodetic datums and CRSs even when the ESRI and EPSG names match.
- 9.8.1 rolls EPSG content back to 12.029 to prevent ETRS89 transformation
  regressions affecting Austria, Belgium, Catalonia, the Netherlands, Romania,
  and Serbia. EPSG datum and CRS records added in 9.8.0, mostly `ETRS89-XXX`
  national realizations, are consequently unavailable.

Do not compare only the numerical PROJ version when investigating a missing
record. Inspect the active database and search path as well.

## ESRI and Legacy Name Handling

- ESRI records intended to be deprecated are marked deprecated again (since
  9.6.2). Enumeration code that filters deprecated objects will see the
  corrected status.
- `ProjectedCRS::identify()` recognizes old ESRI CRS names ending in
  `_IntlFeet` more robustly (since 9.6.2).
- `createObjectsFromName()` tolerates `N`/`S` versus `North`/`South`, a missing
  zone, and a missing height (since 9.6.0).
- Restored legacy EPSG aliases improve recognition of WKT using older names
  (since 9.7.0).
- Older EPSG WKT is identified again after the addition of newer ETRS89
  national-datum definitions (since 9.8.0).

Use tolerant name lookup for recovery and migration, not as a replacement for
authority codes in stored application data.

## Identification Correctness

- `BoundCRS::identify()` avoids constructing an invalid `BoundCRS` for CRSs
  based on NTF (Paris) (since 9.7.1). This prevents later crashes caused by the
  malformed result.
- `ProjectedCRS::identify()` rejects candidates whose ellipsoid differs
  substantially from the input definition (since 9.8.0). A name or projection
  match alone is not enough.
- Coordinate-system codes for IAU2015 North Polar and South Polar CRSs are
  corrected (since 9.7.0).

When identification output changes, compare datum, ellipsoid, coordinate
system, units, and axis directions before treating it as a regression.

## WKT Import and Export

### Import

- A South Orientated Transverse Mercator represented as regular TMerc with
  `Scale_Factor=-1` imports correctly (since 9.6.1).
- WKT2 `DEFININGTRANSFORMATION` parses instead of being rejected (since
  9.7.0), but its contents are ignored. Parsing success does not apply the
  transformation.
- WKT and PROJJSON accept datum ensembles with no members (since 9.7.1).
- WKT1 accepts vertical CRS definitions beginning with
  `VERT_CS["Geoid 2012A",` (since 9.8.0).

### Export

- A spherical Mercator CRS can export to WKT1 as `Mercator_1SP` (since 9.7.0).
- ESRI:54099, `WGS_1984_Spilhaus_Ocean_Map_in_Square`, can export as a PROJ
  string (since 9.6.0).

## PROJJSON Shape

When exporting a Projected CRS, `base_crs` has an explicit `type` member
(since 9.6.0). Its value is `GeographicCRS` or `GeodeticCRS`.

Schema validators and parsers must accept the member and both allowed values.
Avoid assuming that a nested CRS omits its type merely because the containing
object already establishes context.

## Database-Backed Grid and CRS Coverage

- EGM2008 grid-transformation records cover WGS 84 realizations (since 9.6.0).
- Dutch NSGI operations reference `nl_nsgi_nllat2018.tif` and
  `nl_nsgi_bongeo2004.tif` (since 9.7.0). The database reference does not
  guarantee that the grid file is locally installed.
- Czechia transformations defined in `transformations_czechia.sql` are enabled
  (since 9.7.1).
- MTM with CGVD2013 and UTM with CGVD28 are supported for epochs 1997, 2002,
  and 2010 (since 9.8.0).

## Database Migration Checks

1. Record `proj.db` provenance and authority metadata.
2. Check application SQL against new tables and optional columns.
3. Re-run deprecated-object enumeration.
4. Test stored legacy ESRI and EPSG WKT fixtures.
5. Verify required grids separately from database operation records.
6. On 9.8.1, audit dependencies on records introduced only in 9.8.0.
