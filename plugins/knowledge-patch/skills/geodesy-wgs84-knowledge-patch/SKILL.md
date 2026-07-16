---
name: geodesy-wgs84-knowledge-patch
description: WGS 84 current compatibility guidance. Use for WGS 84 work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Geodesy / WGS 84 Knowledge Patch

Baseline: WGS 84 (G2139), ITRF2020, and PROJ through 9.3; covers WGS 84 (G2296), ITRF2020-u2024, PROJ 9.4 through 9.8.1, and related implementation details.

## Use this patch

Before transforming or comparing coordinates, identify all of the following:

- Reference frame or datum realization, not only the label “WGS 84”, “ITRF”, or “ETRS89”.
- Coordinate epoch and parameter reference epoch for dynamic frames.
- Coordinate type, axis order, units, and dimensionality.
- Ellipsoidal, orthometric, dynamic, normal-orthometric, or tidal height semantics.
- Required accuracy, area of use, grid availability, and acceptable fallback behavior.

Then load the relevant reference below. Preserve explicit directions, signs, epochs, and units when transcribing transformation parameters.

## Reference index

| Reference | Topics |
| --- | --- |
| [Reference frames and datums](references/reference-frames-and-datums.md) | WGS 84 (G2296), ITRF2020-u2024, ETRS89, GPS, GLONASS, Galileo, BeiDou |
| [Helmert and datum transformations](references/helmert-and-datum-transformations.md) | PROJ Helmert conventions, kinematic parameters, NGS/HTDP parameters, Molodensky, Molodensky-Badekas, regression transforms |
| [Cartesian and local coordinates](references/cartesian-and-local-coordinates.md) | ECEF inverse conversion, fixed-origin ENU, PROJ topocentric operations |
| [Ellipsoidal geodesics](references/ellipsoidal-geodesics.md) | Vincenty direct/inverse methods, antipodal failures, GeographicLib, spherical and rhumb caveats |
| [Projections and grid references](references/projections-and-grid-references.md) | UTM and Transverse Mercator, Krüger series, convergence and scale, MGRS, South African Lo, OS grid |
| [Vertical datums and geoids](references/vertical-datums-and-geoids.md) | EGM2008, geoid grids, NAVD 88, NGVD 29, tidal datums, IGLD 85 |
| [PROJ pipelines and operation selection](references/proj-pipelines-and-operations.md) | Pipelines, grids, 4D operations, CRS operation selection, coordinate metadata, projection and deformation operations |
| [PROJ deployment and compatibility](references/proj-deployment-and-compatibility.md) | EPSG database rollback, resource embedding and lookup, networking, CLI/API changes, build breaks |
| [pyproj CRS and transformers](references/pyproj-crs-and-transformers.md) | CF/WKT/PROJJSON, dimensional promotion, compound and bound CRSs, transformer selection, errors and streaming |
| [Library-specific behavior](references/library-specific-behavior.md) | GeographicLib C++/Python scope and Movable Type modules, reference frames, n-vectors, DMS formatting |

## Breaking changes and deprecations

### Respect PROJ compatibility boundaries

- PROJ 7 requires C99 and rejects NTv2 grids whose `GS_TYPE` is not `SECONDS`.
- PROJ 8 removes `proj_api.h`.
- PROJ 9 removes Autotools; use CMake. PROJ 9.4 requires CMake 3.16 or newer, and PROJ 9.6 requires C++17 to build.
- Use `PROJ_DATA`, introduced in 9.1, instead of deprecated `PROJ_LIB`.
- Do not use the Helmert `transpose` switch; it has been forbidden since PROJ 5.2. State `coordinate_frame` or `position_vector` explicitly whenever rotations are present.
- Do not use removed deformation `+t_obs`; use `+dt` and supply coordinate time when appropriate.

### Pin behavior-sensitive PROJ versions

- PROJ 9.8.1 deliberately rolls its EPSG database back from 12.049 to 12.029, removing national `ETRS89-XXX` records introduced in 9.8.0. Do not assume the newer patch contains every record from 9.8.0.
- Require at least 9.3.1 for corrected ITRF2008 `dry` values for `EURA` and `EURA_T`, 9.6.0 for the corrected ITRF97 parameter in the ITRF2014 file, and 9.6.1 to prevent NAD83(CSRS) realizations from routing through generic NAD83.
- Expect exact auxiliary-latitude changes in PROJ 9.7.0 to alter results from `aea`, `cea`, `laea`, `eqearth`, `healpix`, and `rhealpix` relative to 9.6 and earlier.
- Treat a WKT2 `DEFININGTRANSFORMATION` node as parsed but ignored by PROJ 9.7; it does not instantiate the transformation.

### Make operation fallback intentional

By default, `proj_trans()` may retry a lower-ranked candidate when the preferred operation fails for a coordinate. Use `ONLY_BEST=YES`, `cs2cs --only-best`, `allow_ballpark=False`, explicit authority and accuracy constraints, and error checking when silent fallback is unacceptable. Verify the operation actually used rather than trusting only the initial candidate description.

When a target CRS is 2D, PROJ 9.1 and newer do not perform a vertical transformation merely because the source is compound. Keep the workflow 3D, or use `cs2cs --3d`, when height must participate.

## Frame and epoch discipline

### Name the WGS 84 realization

WGS 84 (G2296) became current on 7 January 2024, superseding G2139. It is aligned to ITRF2020 and IGS20. For precision work, record G2296 explicitly instead of treating “WGS 84” as timeless.

The aligned operational WGS 84 and ITRF frames have a zero seven-parameter transformation by design. Do not insert another Helmert step solely because the frame names differ.

### Treat ITRF2020-u2024 as updated station data

ITRF2020-u2024 preserves the ITRF2020 origin, scale, and orientation; all transformation parameters between them are zero. Use its updated positions, velocities, discontinuities, post-seismic deformation, and seasonal station-motion products for propagation. Keep an actual observation epoch with every dynamic-frame coordinate.

### Keep broadcast GNSS frames distinct

- GPS broadcast positions are WGS 84.
- GLONASS broadcasts PZ-90.11.
- Galileo broadcasts GTRF.
- BeiDou broadcasts BDC.

Apply realization-appropriate transformations; do not relabel every GNSS result as WGS 84.

## Transformation quick reference

### Use Cartesian coordinates for Helmert operations

For a 3D geographic workflow, convert longitude, latitude, and ellipsoidal height to geocentric coordinates, apply `+proj=helmert`, then convert back. PROJ uses metres for `x/y/z`, arcseconds for `rx/ry/rz`, ppm for `s`, and corresponding per-year units for rates.

```text
P(t) = P(t_epoch) + dP * (t - t_epoch)
```

Supply observation time as the coordinate’s fourth component in decimal years. Negating rotations converts between coordinate-frame and position-vector conventions; it does not invert source and target.

### Keep local frames fixed

For ECEF odometry in a stable ENU frame, choose one origin and reuse its basis for position, velocity, and orientation:

```text
p_enu0 = R_ecef_to_enu0 * (p_ecef - p0_ecef)
v_enu0 = R_ecef_to_enu0 * v_ecef
R_body_to_enu0 = R_ecef_to_enu0 * R_body_to_ecef
```

Do not rebuild the ENU basis at each current position unless a moving local frame is intended.

### Build valid PROJ pipelines

Use at least one `+step`; keep adjacent step units compatible. Use `+inv` to reverse one step and `+omit_fwd` or `+omit_inv` to skip it by whole-pipeline direction. Convert geographic coordinates through `+proj=cart` before `+proj=topocentric`.

```text
+proj=pipeline +ellps=WGS84
+step +proj=cart
+step +proj=topocentric +lon_0=5 +lat_0=55 +h_0=200
```

For grid lists, the first grid covering the point wins. Prefix an optional missing grid with `@`; use a final `null` only when a worldwide zero-shift fallback is intentional.

## Height quick reference

### Distinguish ellipsoidal and gravity-related height

For EGM2008 (`EPSG:3855`):

```text
H_EGM2008 = h_WGS84 - N
h_WGS84 = H_EGM2008 + N
```

`CRS.to_3d()` adds ellipsoidal height; it does not add EGM2008, another geoid model, or an orthometric datum. A vertical CRS identifier alone also does not provide a correction grid.

Do not substitute constant offsets between NAVD 88 and NGVD 29, between tidal and geodetic datums, or between different EGM releases. These are distinct surfaces and, in some cases, distinct height types and epochs.

## Geodesic quick reference

### Prefer globally robust ellipsoidal solvers

Spherical calculations can err by roughly `0.3%`, and about `0.55%` on some equator-crossing routes. Vincenty normally gives high accuracy but its inverse iteration can be slow or fail near antipodes. Bound the iteration, test convergence, handle coincident/equatorial/antipodal degeneracies, and fall back to a globally convergent solver such as GeographicLib.

Do not use spherical Mercator isometric latitude for an ellipsoidal rhumb calculation:

```text
psi = asinh(tan(phi)) - e * atanh(e * sin(phi))
```

## Projection quick reference

### Configure UTM explicitly

`+proj=utm` requires `+zone=1..60`; use `+south` for southern false northing and state `+ellps=WGS84` when needed because a bare projection string defaults to GRS80. The default sixth-order `poder_engsager` algorithm is the safe general choice; `+algo=auto` may select the faster approximation within its error threshold, while `+approx` can diverge beyond about 3° from the central meridian.

Carry zone and hemisphere with every UTM coordinate. Easting/northing alone does not reliably determine the hemisphere. Account for both meridian convergence and point scale in ground-to-grid work, plus elevation reduction for ground distances.

MGRS denotes a cell, not its centre. Conversion routines documented here return the south-west corner, and MGRS text formatting truncates while UTM formatting rounds.

## Python API quick reference

### Preserve CRS structure

Use WKT2:2019 or PROJJSON when lossless structure matters; PROJ strings and parameter dictionaries can discard CRS information. Treat bound and compound CRSs recursively, and do not replace a bound CRS with the authority code of only its source CRS.

### Make transformer behavior explicit

```python
transformer = Transformer.from_crs(
    source_crs,
    target_crs,
    authority="EPSG",
    allow_ballpark=False,
)
x2, y2 = transformer.transform(x, y, errcheck=True)
used = transformer.get_last_used_operation()
```

Omitting `authority` applies configured authority-to-authority preferences; `authority="any"` removes those restrictions. Transformation errors otherwise return `inf` by default. For streamed three-component time coordinates, set `time_3rd=True`; otherwise the third ordinate is height.

Do not share `TransformerGroup`-returned operations or transformers concurrently. For `inplace=True`, provide C-contiguous double-precision arrays.
