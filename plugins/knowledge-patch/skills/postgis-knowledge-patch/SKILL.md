---
name: postgis-knowledge-patch
description: PostGIS 3.6.1 compatibility. Use for PostGIS work.
license: MIT
version: 3.6.1
metadata:
  author: Nevaberry
---

# PostGIS Knowledge Patch

Use this skill before changing PostGIS schemas, extension versions, spatial SQL,
loaders, or build configuration. Start with the upgrade checks below, then open
the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and upgrades](references/compatibility-and-upgrades.md) | PostgreSQL, GEOS, PROJ, SFCGAL, and GDAL requirements; build changes; replaced SQL signatures; supported patch lines |
| [Geometry and processing](references/geometry-and-processing.md) | Operators, predicates, RelateNG, accessors, coverage cleaning, display simplification, and SFCGAL operations |
| [Loaders, CLI, and Tiger](references/loaders-cli-and-tiger.md) | Database-wide `postgis` commands, Tiger packaging and upgrades, loader behavior, and address parsing |
| [Raster and GDAL](references/raster-and-gdal.md) | Touched-pixel clipping, raster aggregates and remapping, intersection fractions, and GDAL diagnostics |
| [Topology](references/topology.md) | TopoGeometry comparison, shared sequences, bigint identifiers, corruption repair, precision, size, and import administration |

## Handle upgrade-sensitive changes first

### Rebuild objects that depend on replaced SQL functions

Treat a function replacement as an object-identity change, even when familiar
calls still parse.

- Rebuild views and materialized views that call the record overload of
  `ST_AsGeoJSON`; its signature changed so a column can supply the feature ID.
- Rebuild materialized views that call any `ST_Clip` overload; all variants
  were replaced.
- Check other stored expressions and prepared deployment SQL for overload
  assumptions before completing the extension upgrade.

See [Compatibility and upgrades](references/compatibility-and-upgrades.md) for
the associated build, packaging, and metadata-discovery changes.

### Repair TopoGeometry columns after the affected upgrade

An upgrade of `postgis_topology` through the initial affected release can
corrupt registered TopoGeometry columns. After installing a release that
contains the repair routine, repair every registered column:

```sql
SELECT topology.FixCorruptTopoGeometryColumn(
         schema_name, table_name, feature_column
       )
FROM topology.layer;
```

Run this deliberately as a repair step; do not assume that updating the
extension alone repairs existing column metadata. Read
[Topology](references/topology.md) before changing topology domains or
identifier types.

### Use patch accessors for TIN and PolyhedralSurface

`ST_NumGeometries` and `ST_GeometryN` now treat a TIN or
`PolyhedralSurface` as one geometry. Do not use those functions to enumerate
patches. Use:

```sql
SELECT ST_NumPatches(surface);
SELECT ST_PatchN(surface, patch_number);
```

Audit code that inferred patch counts or extracted patches through generic
collection accessors.

### Account for geometry-column metadata discovery

The initial 3.6.0 release stopped parsing constraints in the
`geometry_columns` view. Constraint parsing returned in 3.6.1. If tooling was
built or tested against unpatched 3.6.0, recheck its discovery results after
updating rather than treating the temporary behavior as stable.

### Migrate the Tiger geocoder explicitly

The standalone Tiger extension no longer adds `tiger` to the database search
path. Schema-qualify geocoder objects or set the path in the calling context.
Upgrade normally:

```sql
ALTER EXTENSION postgis_tiger_geocoder UPDATE;
```

If PostgreSQL reports that no update path exists, or the installed extension
is a development build, bridge through the special version first:

```sql
ALTER EXTENSION postgis_tiger_geocoder UPDATE TO "ANY";
ALTER EXTENSION postgis_tiger_geocoder UPDATE;
```

Read [Loaders, CLI, and Tiger](references/loaders-cli-and-tiger.md) for version
requirements, packaging, schema, indexing, and parser changes.

## Adjust for changed geometry behavior

### Compare geometry and TopoGeometry deliberately

Geometry has an explicit `<>` operator, eliminating the former non-unique
operator failure for `<>` and `!=`. TopoGeometry inequality is now ambiguous.
To reproduce its former structural comparison, compare all components:

```sql
id(tg1) <> id(tg2)
OR topology_id(tg1) <> topology_id(tg2)
OR layer_id(tg1) <> layer_id(tg2)
OR type(tg1) <> type(tg2)
```

### Recheck predicates and measurements

- Interpret `ST_DFullyWithin(A, B, R)` as
  `ST_Contains(ST_Buffer(A, R), B)`.
- Expect `ST_Length` to return `0` for a `CurvePolygon`.
- With GEOS 3.13, expect relate matrices to differ for the multi-valent
  endpoint boundary-node rule.
- Make invalid `MultiPolygon` inputs with shared boundaries valid before
  relating them.
- Expect a zero-length `LineString` to relate like its equivalent `Point`.

### Do not assume old deterministic or out-of-plane results

- Regenerate fixtures whose exact seeded `ST_GeneratePoints` sequence matters;
  the optimized implementation changed the pseudorandom output.
- Starting with 3.5.1, expect `ST_TileEnvelope` to clip envelopes to the tile
  plane instead of returning bounds outside it.

## Use the new processing APIs

### Clean polygon coverages as a window operation

Use `ST_CoverageClean` with GEOS 3.14 or newer to turn a dirty polygonal
coverage into edge-matched, non-overlapping polygons:

```sql
SELECT id,
       ST_CoverageClean(
         geom, 0.5, -1, 'MERGE_LONGEST_BORDER'
       ) OVER () AS geom
FROM parcels;
```

Interpret `gapMaximumWidth` as the largest gap to close. Leave
`snappingDistance` at `-1` to choose it automatically, or use `0` to disable
snapping. Choose overlap assignment from `MERGE_LONGEST_BORDER` (default),
`MERGE_MAX_AREA`, `MERGE_MIN_AREA`, or `MERGE_MIN_INDEX`.

### Prefer purpose-built geometry utilities

- Use `ST_CurveN` and `ST_NumCurves` for consistent curved-geometry access.
- Use `ST_RemoveIrrelevantPointsForView` and `ST_RemoveSmallParts` to reduce
  geometries intended for display.
- Use patch-specific accessors for TIN and polyhedral surfaces.

### Move SFCGAL calls to the CG namespace

Prefer the `CG_` names; the old SFCGAL-backed `ST_` names are deprecated. For
example, replace `ST_StraightSkeleton` with `CG_StraightSkeleton`. Its optional
parameter uses M as distance in the result. Review the complete operation list
and library requirements in
[Geometry and processing](references/geometry-and-processing.md).

### Select the new raster operation by intent

- Pass the `touched` option to raster `ST_Clip` when every pixel touched by the
  input geometry should participate.
- Use `ST_AsRasterAgg` to aggregate geometries into raster output.
- Use `ST_ReclassExact` for fast exact-value remapping.
- Use `ST_IntersectionFractions` only with GEOS 3.14 or newer.
- Remove calls that depended on the deleted ambiguous
  `ST_ApproxQuantile(raster, double precision)` signature.

See [Raster and GDAL](references/raster-and-gdal.md) for details.

## Operate and diagnose installations

Use the `postgis` script for database-wide discovery and upgrades:

```text
postgis list-enabled
postgis list-all
postgis status
postgis upgrade
```

`status` reports across databases, and `upgrade` upgrades every database that
needs it. Do not assume either command is limited to the current database.

Enable GDAL CPL diagnostics through PostgreSQL logging when investigating
raster-driver behavior:

```sql
SET postgis.gdal_cpl_debug = ON;
```

Confirm runtime and build dependencies before enabling features. In
particular, GEOS 3.14 is required for the complete current feature set, while
some SFCGAL and raster capabilities have their own minimum library versions.
Use the compatibility reference as the authoritative checklist.
