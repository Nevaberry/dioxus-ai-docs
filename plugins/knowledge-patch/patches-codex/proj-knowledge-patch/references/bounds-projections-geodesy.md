# Bounds, Projections, and Geodesy

## Bounds Transformation APIs

`proj_trans_bounds()` supports a CompoundCRS target (since 9.6.0).
`proj_trans_bounds_3D()` was added at the same time for three-dimensional
bounds.

Further fixes affect which extrema are returned:

- Points within the source grid are sampled to avoid missing transformed
  extrema (since 9.6.2). This includes worldwide EPSG:4326 bounds transformed
  to ESRI:54099.
- A `PJ*` created directly from a PROJ pipeline no longer triggers errors in
  affected `proj_trans_bounds()` cases (since 9.6.2).
- Geographic bounds crossing the antimeridian can again be transformed to a
  projected CRS (since 9.7.0), fixing a regression introduced in 9.6.2.

When maintaining snapshot tests, expect corrected output to expand a box if
interior samples reveal extrema that edge-only sampling missed.

## Bounds Test Matrix

Include:

- a normal projected envelope;
- a geographic envelope crossing the antimeridian;
- worldwide EPSG:4326 to ESRI:54099;
- a directly constructed pipeline object;
- a compound target CRS; and
- a 3D envelope through `proj_trans_bounds_3D()`.

Record densification inputs, axis conventions, and the chosen operation so
different sampling assumptions are not mistaken for regressions.

## New Projection Support

PROJ adds the Airocean projection, formerly called Dymaxion, and the Spilhaus
projection (since 9.6.0). ESRI:54099 represents
`WGS_1984_Spilhaus_Ocean_Map_in_Square`.

The ellipsoidal Equidistant Cylindrical method EPSG:1028 is supported (since
9.8.0). Do not substitute a spherical formula when the CRS calls for this
ellipsoidal method.

## Corrected Projection Results

- Wagner VI parameters are corrected (since 9.6.1), so transformed coordinates
  can differ from earlier output.
- Inverse conversion from authalic latitude to geographic latitude is exact
  for `+proj=aea`, `cea`, `laea`, `eqearth`, `healpix`, and `rhealpix` (since
  9.7.0). Rebaseline inverse-roundtrip expectations where prior approximations
  leaked into fixtures.
- Spherical `tmerc` is numerically stable at `lat=lat_0` (since 9.8.0).
  Include the latitude of origin in regression tests.

Before accepting numeric drift, confirm ellipsoid, units, axis order, and
pipeline. These corrections do not justify a blanket increase in tolerance.

## Direct and Inverse Geodesics

`proj_geod_direct()` performs a direct geodesic calculation using a `PJ`
transformation object (since 9.7.0). Use a compatible geodetic object and follow
the API’s coordinate and angular-unit conventions.

Geodesic inverse calculation supports meridional points on a prolate ellipsoid
(since 9.7.0). Tests should include points on a shared meridian and an explicitly
prolate ellipsoid rather than exercising only oblate Earth ellipsoids.

## Numerical Review Checklist

1. Capture the exact CRS and operation pipeline.
2. Confirm whether the calculation is spherical or ellipsoidal.
3. Test forward/inverse round trips away from and at singular-looking cases.
4. Include interior sampling when validating bounds.
5. Exercise antimeridian and worldwide envelopes.
6. Use tighter, evidence-based tolerances after comparing corrected formulas.
