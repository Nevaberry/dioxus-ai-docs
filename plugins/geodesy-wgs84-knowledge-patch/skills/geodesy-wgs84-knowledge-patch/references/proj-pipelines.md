# PROJ Pipelines & Helmert Transforms

## Pipeline Syntax

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

## Helmert Conventions

- `coordinate_frame` (EPSG 1032/9607) = clockwise rotation of frame
- `position_vector` (EPSG 1033/9606) = counter-clockwise rotation
- Switch between them by negating rx, ry, rz (and rates)

## 14-Parameter Kinematic Helmert

Adds `+dx +dy +dz +ds +drx +dry +drz +t_epoch` for time-dependent transforms (ITRF↔ITRF).

## Topocentric Transform (PROJ 8.0+)

ECEF→ENU via PROJ:

```bash
echo 3771793.97 140253.34 5124304.35 2020 | \
  cct +proj=topocentric +X_0=3652755.31 +Y_0=319574.68 +Z_0=5201547.35
```
