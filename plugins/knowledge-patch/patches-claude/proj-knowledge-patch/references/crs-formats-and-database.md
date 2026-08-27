# CRS Formats, Authority Data, and Identification

## Database revision matrix

Treat the database revision as part of the runtime, not merely a property of
the linked library:

| PROJ release | Bundled authority content |
| --- | --- |
| 9.6.0 | EPSG 12.004, including engineering datum/CRS records |
| 9.6.1 | EPSG 12.012 and ESRI definitions from ArcGIS Pro 3.5 |
| 9.6.2 | EPSG 12.013 |
| 9.7.0 | EPSG 12.022 |
| 9.7.1 | EPSG 12.029 |
| 9.8.0 | EPSG 12.049 and ArcGIS Pro 3.6 ESRI records |
| 9.8.1 | EPSG 12.029 after rollback from 12.049 |

The 9.8.1 rollback avoids regressions in ETRS89 transformations affecting
Austria, Belgium, Catalonia, the Netherlands, Romania, and Serbia. EPSG datum
and CRS records introduced with 9.8.0—mostly `ETRS89-XXX` national
realizations—are consequently unavailable in the bundled 9.8.1 database.
Diagnose lookup and operation differences against this matrix before changing
application code.

## Schema and method coverage

The database adds these capabilities (since 9.6.0):

- Deprecated ESRI names are ingested to improve old ESRI WKT import.
- `engineering_datum` and `engineering_crs` tables carry related EPSG records.
- `concatenated_operation_step.step_direction` is optional and records a step's
  direction when present.
- EPSG “Vertical Offset by Grid Interpolation (asc)” maps to
  `+proj=vgridshift`.
- Full-matrix coordinate-frame rotation methods are recognized for geocentric
  and geographic-2D coordinates.
- JSON TIN interpolation methods are recognized for Cartesian-grid offsets and
  vertical offsets.

Do not make schema consumers require `step_direction`; it is optional. When
generating or inspecting pipelines, account for the newly recognized method
families instead of treating them as unknown operations.

## Authority status, aliases, and supplied grids

- ESRI records intended to be deprecated are marked deprecated again (since
  9.6.2). Enumeration and filtering should use the corrected status.
- Alias rows removed from newer EPSG releases are restored for older names
  (since 9.7.0), improving WKT recognition.
- The database references `nl_nsgi_nllat2018.tif` and
  `nl_nsgi_bongeo2004.tif` for their Dutch NSGI operations (since 9.7.0).
  Ensure those grids are installed, embedded, or downloadable when choosing
  the corresponding operations.
- IAU2015 North Polar and South Polar CRS coordinate-system codes are corrected
  (since 9.7.0). Refresh fixtures that asserted the earlier codes.
- Czechia operations defined in `transformations_czechia.sql` are enabled
  (since 9.7.1) and are available to discovery.
- ESRI aliases for geodetic datums and CRSs are created even when an ESRI name
  matches its EPSG counterpart (since 9.8.0).

## PROJJSON

Projected CRS export includes an explicit `type` member under `base_crs` (since
9.6.0). Accept either:

```json
{
  "base_crs": {
    "type": "GeographicCRS"
  }
}
```

or a `type` value of `GeodeticCRS`, according to the base CRS. Update strict
schemas, canonical serializers, and structural test fixtures to retain or
accept the member.

WKT and PROJJSON import accept datum ensembles with no members (since 9.7.1).
Allow the empty collection even if an application-level policy later rejects
it for a particular operation.

## WKT import

- Interpret a South Orientated Transverse Mercator represented as regular TMerc
  with `Scale_Factor=-1` (since 9.6.1). Do not normalize away the sign before
  PROJ imports the definition.
- Accept WKT2 `DEFININGTRANSFORMATION` syntax (since 9.7.0), but remember that
  PROJ ignores its contents. If the transformation must be applied, construct
  or select it separately rather than relying on parser acceptance.
- Accept WKT1 vertical definitions beginning with
  `VERT_CS["Geoid 2012A",` (since 9.8.0).

## WKT export

A Mercator (Spherical) CRS defined on a sphere exports to WKT1 as
`Mercator_1SP` (since 9.7.0). Consumers comparing generated WKT text should
allow that representation and compare semantic CRS content where possible.

ESRI:54099 (`WGS_1984_Spilhaus_Ocean_Map_in_Square`) can export as a PROJ
string (since 9.6.0).

## Name lookup and identification

- `ProjectedCRS::identify()` recognizes old ESRI names ending in `_IntlFeet`
  more robustly (since 9.6.2).
- `createObjectsFromName()` tolerates `N`/`S` versus `North`/`South`, a missing
  zone, and a missing height (since 9.6.0).
- `BoundCRS::identify()` avoids constructing an invalid `BoundCRS` for an NTF
  (Paris)-based CRS (since 9.7.1), preventing later crashes from that malformed
  result.
- `ProjectedCRS::identify()` rejects candidates whose ellipsoid differs
  substantially from the input definition (since 9.8.0).
- Identification again recognizes older EPSG WKT after newer national
  ETRS89-datum definitions are added (since 9.8.0).

Prefer authority codes for stable storage. Use tolerant lookup for ingestion,
then serialize the identified object rather than preserving an ambiguous input
name as the only identity.
