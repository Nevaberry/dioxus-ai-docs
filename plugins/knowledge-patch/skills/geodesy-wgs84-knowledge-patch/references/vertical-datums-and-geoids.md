# Vertical Datums and Geoids

## EGM2008 height semantics

`EPSG:3855` identifies EGM2008 gravity-related height `H` in metres with an up axis. Its zero surface approximates mean sea level from EGM2008 applied to the WGS 84 ellipsoid, and it replaces EGM96 height `EPSG:5773`.

For WGS 84 ellipsoidal height `h` and EGM2008 geoid undulation `N`, preserve the sign convention:

```text
H_EGM2008 = h_WGS84 - N
h_WGS84 = H_EGM2008 + N
```

The legacy PROJ.4 export for `EPSG:3855` is only `+vunits=m +no_defs +type=crs`. It identifies the vertical CRS but provides neither a geoid grid nor a height-correction operation.

Do not treat the EGM2008 zero surface as local tide-gauge mean sea level. Local mean sea level can differ from an equipotential surface by a metre or more.

## EGM2008 grid contract

The 1-minute WGS 84 tide-free, small-endian grid `Und_min1x1_egm2008_isw=82_WGS84_TideFree_SE` has `10801` rows by `21600` columns of 4-byte IEEE floating-point undulations. Resolution, byte order, ellipsoid, and tide system are part of the contract, not interchangeable implementation details.

EGM2008 is complete through spherical-harmonic degree and order 2159, with extra coefficients through degree 2190 and order 2159. Both 2.5-minute and 1-minute grids are available. A 16-bit PGM representation introduces up to about `0.3 mm` of quantization relative to floating-point grid data.

## Distinct EGM releases

- EGM84 is degree and order 180 with a 30-minute raster.
- EGM96 is degree and order 360 with a 15-minute raster.
- EGM2008 uses the higher-resolution model and grids described above.

Each release has its own EPSG vertical datum. Do not relabel EGM84 or EGM96 height as EGM2008 height merely because all are WGS 84 gravitational models.

## NAVD 88 and NGVD 29

NAVD 88 is anchored by an adopted elevation at Point Rimouski and reports Helmert orthometric heights. NGVD 29 held 26 tide gauges fixed and reports normal orthometric heights.

Their discrepancy is a gravity-related complex surface, not a constant offset or tilt. Neither datum is exactly local mean sea level or the idealized global geoid. Use an appropriate surface transformation.

## Tidal datums

Tidal datums such as MLLW, MLW, MHW, and MHHW are local surfaces tied to nearby monuments and reduced over a designated 19-year National Tidal Datum Epoch. They describe different statistics of the daily tide. Do not infer them from a horizontal datum or convert them to ellipsoidal or geoid height with a universal offset.

## IGLD 85 and NAVD 88

IGLD 85 and NAVD 88 share the Father’s Point reference zero and the same benchmark geopotential numbers. IGLD 85 publishes dynamic heights, while NAVD 88 publishes Helmert orthometric heights. The common reference does not make their reported values interchangeable.
