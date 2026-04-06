---
name: postgis-knowledge-patch
description: "PostGIS changes since training cutoff (latest: 3.6.1) — SFCGAL CG_* rename, ST_CoverageClean, ST_AsRasterAgg, topology bigint IDs, viewport simplification, 3D SFCGAL ops. Load before working with PostGIS."
license: MIT
version: "3.6.1"
metadata:
  author: Nevaberry
---

# PostGIS 3.5+ Knowledge Patch

Claude's baseline knowledge covers PostGIS through 3.4. This skill provides features from 3.5 (Sep 2024) onwards.

**Source**: PostGIS news at https://postgis.net/news/

## Additional Resources

### Reference Files

For detailed descriptions, code examples, and full context on each change, consult:
- **`references/postgis-3.5-3.6-details.md`** — Detailed changelog organized by topic (breaking changes, new vector/raster/topology/SFCGAL functions)

## 3.5.0 (2024-09-25)

**Requires**: PostgreSQL 12-17, GEOS 3.8+, Proj 6.1+. SFCGAL 1.5 for all SFCGAL features.

### Breaking Changes
| Change | Impact |
|--------|--------|
| SFCGAL `ST_*` → `CG_*` prefix | All SFCGAL functions renamed. Old `ST_` names deprecated. |
| `ST_DFullyWithin` semantics | Now `ST_Contains(ST_Buffer(A, R), B)`. May return different results. |
| `ST_AsGeoJSON(record)` signature | Can promote column as Feature `id`. Materialized views need rebuild. |
| `ST_GeneratePoints` seed | Seeded random points produce different results. Regenerate if needed. |
| `ST_Clip` variants replaced | New `touched` param added. Materialized views need rebuild. |

### New Functions
| Function | Purpose |
|----------|---------|
| `ST_HasZ(geom)` / `ST_HasM(geom)` | Boolean Z/M dimension checks |
| `ST_CurveN(geom, n)` / `ST_NumCurves(geom)` | CompoundCurve accessors |
| `ST_RemoveIrrelevantPointsForView(geom, ...)` | Viewport-based simplification |
| `ST_RemoveSmallParts(geom, ...)` | Remove small polygon parts (slivers) |
| `TopoGeo_LoadGeometry(topo, geom, tol)` | Load geometry into topology |
| `CG_Visibility(polygon, point)` | Visibility polygon (SFCGAL) |
| `CG_*Partition` functions | Polygon partitioning algorithms (SFCGAL) |
| `ST_ExtrudeStraightSkeleton(geom)` | Extrude along straight skeleton (SFCGAL) |

### ST_Clip `touched` (Raster)
```sql
-- Include pixels touched by geometry, not just centers-inside
SELECT
  ST_Clip (rast, geom, touched => true)
FROM
  raster_table;
```

## 3.5.1 (2024-12-22)

**Breaking**: `ST_TileEnvelope` now clips envelopes to tile plane extent. Edge tiles return smaller geometries than before.

## 3.6.0 (2025-09-01)

**Requires**: PostgreSQL 12-18, GEOS 3.8+, Proj 6.1+. GEOS 3.14+ for full features. SFCGAL 2.2+ for all SFCGAL features.

### Breaking Changes
| Change | Impact |
|--------|--------|
| TIN/PolyhedralSurface accessors | `ST_NumGeometries`/`ST_GeometryN` return 1. Use `ST_NumPatches`/`ST_PatchN` instead. |
| Topology bigint | Topology IDs now `bigint`. Integer functions replaced with bigint versions. |
| `st_approxquantile(raster, double precision)` | Removed (ambiguous). Use variant with additional params. |

### New Functions
| Function | Purpose |
|----------|---------|
| `ST_CoverageClean(geom[])` | Clean polygonal coverage — edge match + gap removal (GEOS 3.14) |
| `ST_AsRasterAgg(...)` | Aggregate: create raster from geometries |
| `ST_ReclassExact(rast, ...)` | Remap exact values in raster |
| `ST_IntersectionFractions(rast, geom)` | Raster pixel/geometry intersection fractions (GEOS 3.14) |
| `ValidateTopologyPrecision` / `MakeTopologyPrecise` | Topology precision validation and repair |

### New SFCGAL Functions (SFCGAL 2.2)
| Function | Purpose |
|----------|---------|
| `CG_Simplify` | 3D geometry simplification |
| `CG_3DAlphaWrapping` | Tight 3D surface around point set |
| `CG_Scale` / `CG_Translate` / `CG_Rotate` | 3D affine transformations |
| `CG_Buffer3D` | 3D buffering |
| `CG_StraightSkeletonPartition` | Partition polygon via straight skeleton |

SFCGAL now supports M coordinates (SFCGAL >= 1.5.0).

