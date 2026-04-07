---
name: geodesy-wgs84-knowledge-patch
description: "Geodesy & WGS84 reference (latest: 1.0.0) — ECEF↔geodetic/ENU/NED conversions, PROJ pipelines, Helmert transforms, pyproj patterns. Load before working with coordinate transformations."
version: "1.0.0"
license: MIT
metadata:
  author: Nevaberry
---

# Geodesy & WGS84 Knowledge Patch

Essential reference for WGS84 coordinate systems, conversions, datum transformations, and geodetic computation patterns.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Coordinate conversions | [references/coordinate-conversions.md](references/coordinate-conversions.md) | Olson's ECEF→geodetic (~3 nm), ECEF↔ENU/NED rotation |
| pyproj patterns | [references/pyproj-patterns.md](references/pyproj-patterns.md) | UTM lookup, 3D CRS, TransformerGroup, 4D epoch, geodesic |
| PROJ pipelines & Helmert | [references/proj-pipelines.md](references/proj-pipelines.md) | Pipeline syntax, Helmert conventions, kinematic, topocentric |

---

## Key EPSG Codes

| Code | CRS | Notes |
|------|-----|-------|
| 4326 | WGS84 2D geographic (lat/lon) | Most common |
| 4979 | WGS84 3D geographic (lat/lon/height) | Use for ellipsoidal height |
| 4978 | WGS84 geocentric (XYZ ECEF) | Cartesian |
| 4258 | ETRS89 2D geographic | Europe |
| 4937 | ETRS89 3D geographic | Europe with height |
| 3035 | ETRS89 LAEA Europe | EU-recommended projected CRS |
| 3855 | EGM2008 geoid height | Vertical CRS, ~10 cm accuracy |
| 7789 | ITRF2014 3D | Reference frame |
| 9988 | ITRF2020 geocentric | Current ITRF |

## ECEF ↔ ENU Rotation Matrix

The rotation from ECEF difference vector to ENU (φ=latitude, λ=longitude):

```
      ┌ -sin(λ)            cos(λ)           0      ┐
R  =  │ -cos(λ)·sin(φ)    -sin(λ)·sin(φ)   cos(φ) │
      └  cos(λ)·cos(φ)     sin(λ)·cos(φ)   sin(φ) ┘

[E, N, U]ᵀ = R · [Δx, Δy, Δz]ᵀ    where Δ = point_ECEF - ref_ECEF
```

ENU→ECEF uses transpose Rᵀ. For NED, swap rows: row1→N(row2), row2→E(row1), row3→-U.

## Olson's Closed-Form ECEF → Geodetic

Non-iterative, ~3 nm accuracy. Avoids the iterative Bowring method and handles polar/equatorial edge cases through the `c2 > 0.3` branch selection.

```java
a  = 6378137.0;              e2 = 6.6943799901377997e-3;
a1 = 4.2697672707157535e+4;  a2 = 1.8230912546075455e+9;
a3 = 1.4291722289812413e+2;  a4 = 4.5577281365188637e+9;
a5 = 4.2840589930055659e+4;  a6 = 9.9330562000986220e-1;

lon = atan2(y, x);
zp = abs(z); w2 = x*x + y*y; w = sqrt(w2);
r2 = w2 + z*z; r = sqrt(r2);
s2 = z*z/r2; c2 = w2/r2; u = a2/r; v = a3 - a4/r;
if (c2 > 0.3) { s = (zp/r)*(1 + c2*(a1+u+s2*v)/r); lat = asin(s); ss=s*s; c=sqrt(1-ss); }
else           { c = (w/r)*(1 - s2*(a5-u-c2*v)/r); lat = acos(c); ss=1-c*c; s=sqrt(ss); }
g = 1-e2*ss; rg = a/sqrt(g); rf = a6*rg;
u = w-rg*c; v = zp-rf*s; f = c*u+s*v; m = c*v-s*u; p = m/(rf/g+f);
lat += p; alt = f + m*p/2;
if (z < 0) lat = -lat;
```

See [references/coordinate-conversions.md](references/coordinate-conversions.md) for additional context.

## WGS84 Realizations ↔ ITRF

| WGS84 Realization | Year | Aligned to |
|---|---|---|
| G730 | 1994 | ITRF91/92 |
| G873 | 1997 | ITRF94/96 |
| G1150 | 2002 | ITRF2000 |
| G1674 | 2012 | ITRF2008 |
| G1762 | 2013 | ~ITRF2008/14 (≤1 cm RMS) |
| G2139 | 2021 | ITRF2014/IGb14 |
| G2296 | 2024 | ITRF2020/IGS20 (current) |

**Key facts:** The 7-parameter WGS84↔ITRF transform is zero by design. NAD83 is fixed to North American plate and now differs from WGS84/ITRF by ~1-2 m (drifting ~10-20 mm/yr). ETRS89 is fixed to Eurasian plate, drifting ~25 mm/yr from ITRF.

## Vincenty vs GeographicLib

Vincenty's formulae: ~0.5 mm accuracy on the ellipsoid, but **fail to converge on nearly-antipodal points** (>19,936 km). GeographicLib (Karney's algorithm) always converges with nanometer accuracy. Use `pyproj.Geod` (which uses GeographicLib internally) or the `geographiclib` Python package directly.

## pyproj Quick Reference

```python
from pyproj import CRS, Transformer, Geod
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from pyproj.transformer import TransformerGroup

# Find UTM zone for a point
utm_list = query_utm_crs_info(
    datum_name="WGS 84",
    area_of_interest=AreaOfInterest(
        west_lon_degree=-93.58, south_lat_degree=42.03,
        east_lon_degree=-93.58, north_lat_degree=42.03,
    ),
)
utm_crs = CRS.from_epsg(utm_list[0].code)

# Promote 2D CRS to 3D for proper height handling
t = Transformer.from_crs(CRS("EPSG:4326").to_3d(), CRS("EPSG:2056").to_3d(), always_xy=True)

# Explore available transformations
tg = TransformerGroup("EPSG:4326", "EPSG:2964")
tg.best_available                    # True if best transform is available
tg.unavailable_operations[0].grids   # missing grid files

# From PROJ pipeline or EPSG operation code
t = Transformer.from_pipeline("EPSG:1671")
t = Transformer.from_pipeline("+proj=pipeline +step +proj=cart ...")

# 4D with epoch (ITRF2014 → ETRF2014)
t = Transformer.from_crs(7789, 8401)
t.transform(xx=3496737.27, yy=743254.45, zz=5264462.96, tt=2019.0)

# Geodesic calculations
geod = Geod(ellps="WGS84")
total_length = geod.line_length(lons, lats)               # metres
area, perim = geod.polygon_area_perimeter(lons, lats)     # m², m
geod.geometry_length(shapely_linestring)                   # Shapely integration
geod.geometry_area_perimeter(shapely_polygon)
```

See [references/pyproj-patterns.md](references/pyproj-patterns.md) for detailed examples of each pattern.

## PROJ Pipelines and Helmert

Pipeline chains multi-step transforms. Params before first `+step` are global.

```bash
# Datum shift: geodetic (intl ellipsoid) → Helmert → geodetic (GRS80)
proj=pipeline
step proj=cart ellps=intl
step proj=helmert convention=coordinate_frame \
     x=-81.0703 y=-89.3603 z=-115.7526 \
     rx=-0.48488 ry=-0.02436 rz=-0.41321 s=-0.540645
step proj=cart inv ellps=GRS80
```

Helmert conventions: `coordinate_frame` (EPSG 1032/9607) = clockwise rotation of frame. `position_vector` (EPSG 1033/9606) = counter-clockwise. Switch between them by negating rx, ry, rz (and rates).

14-parameter kinematic Helmert adds `+dx +dy +dz +ds +drx +dry +drz +t_epoch` for time-dependent transforms (ITRF↔ITRF).

**Topocentric (ECEF→ENU) in PROJ 8.0+:**
```bash
echo 3771793.97 140253.34 5124304.35 2020 | \
  cct +proj=topocentric +X_0=3652755.31 +Y_0=319574.68 +Z_0=5201547.35
```

See [references/proj-pipelines.md](references/proj-pipelines.md) for detailed pipeline construction.

## Reference Files

| File | Contents |
|---|---|
| [coordinate-conversions.md](references/coordinate-conversions.md) | Olson's closed-form ECEF→geodetic algorithm, ECEF↔ENU/NED rotation |
| [pyproj-patterns.md](references/pyproj-patterns.md) | Advanced pyproj: UTM, 3D CRS, TransformerGroup, pipelines, 4D epoch, geodesic+Shapely |
| [proj-pipelines.md](references/proj-pipelines.md) | PROJ pipeline syntax, Helmert conventions, 14-param kinematic, topocentric |
