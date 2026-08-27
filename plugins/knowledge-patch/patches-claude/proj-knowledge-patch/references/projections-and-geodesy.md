# Projections and Geodesy

## Added projections and methods

- Airocean, formerly called Dymaxion, and Spilhaus projections are available
  (since 9.6.0).
- ESRI:54099 identifies
  `WGS_1984_Spilhaus_Ocean_Map_in_Square` and can be exported as a PROJ string
  (since 9.6.0).
- The ellipsoidal Equidistant Cylindrical operation method EPSG:1028 is
  supported (since 9.8.0).

Use authority definitions where available. When persisting a raw PROJ string,
also retain the CRS identity so a future import does not depend only on a
projection nickname.

## Corrected projection behavior

### Wagner VI

Wagner VI projection parameters are corrected (since 9.6.1). Coordinate
results derived from the earlier parameters can change. Recompute reference
coordinates instead of increasing test tolerances around old results.

### Authalic latitude inversion

Inverse conversion from authalic latitude to geographic latitude is exact for
these projections (since 9.7.0):

- `+proj=aea`
- `+proj=cea`
- `+proj=laea`
- `+proj=eqearth`
- `+proj=healpix`
- `+proj=rhealpix`

Expect inverse results to differ from earlier approximations. Test forward and
inverse round trips near the operating domain's difficult latitudes.

### Spherical Transverse Mercator

Spherical `tmerc` is numerically stable at `lat=lat_0` (since 9.8.0). Remove
workarounds that perturb points away from the latitude of origin only after
confirming all deployed PROJ versions contain the correction.

## Geodesic APIs and ellipsoid cases

Use `proj_geod_direct()` to perform a direct geodesic calculation with a `PJ`
transformation object (since 9.7.0). Keep object construction, angular units,
and result interpretation consistent with the rest of the calling API.

Geodesic inverse calculations support meridional points on a prolate ellipsoid
(since 9.7.0). Retest special-case code that previously rejected, bypassed, or
approximated that geometry.

## Numerical-change triage

1. Confirm the same CRS definitions and authority database.
2. Compare the complete operation pipelines.
3. Determine whether a corrected projection or inverse is involved.
4. Test with exact inputs, units, axis order, and epoch.
5. Recompute authoritative fixtures with the corrected implementation.
6. Retain a regression case at the boundary that exposed the old behavior.
