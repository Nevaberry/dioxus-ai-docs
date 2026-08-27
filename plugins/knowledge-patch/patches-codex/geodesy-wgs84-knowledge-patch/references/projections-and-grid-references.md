# Projections and Grid References

## Contents

- [PROJ Transverse Mercator and UTM](#proj-transverse-mercator-and-utm)
- [Sixth-order Krüger forward conversion](#sixth-order-krüger-forward-conversion)
- [Sixth-order Krüger inverse conversion](#sixth-order-krüger-inverse-conversion)
- [Movable Type UTM behavior](#movable-type-utm-behavior)
- [MGRS cells and formatting](#mgrs-cells-and-formatting)
- [South African Lo coordinates](#south-african-lo-coordinates)
- [OS grid references](#os-grid-references)

## PROJ Transverse Mercator and UTM

For both `+proj=tmerc` and `+proj=utm`, PROJ defaults to the sixth-order `poder_engsager` algorithm. It has full double-precision accuracy within 3,900 km of the central meridian and error below 0.1 mm within 7,000 km.

`+algo=auto`, available since PROJ 7.1, uses the faster Evenden-Snyder method only where estimated error remains below 0.1 mm. `+approx`, available since PROJ 6.0, forces that legacy method, which diverges beyond roughly 3° from the central meridian. `+approx` and `+algo` are mutually exclusive.

`+proj=utm` does not choose a zone from each input coordinate. Supply `+zone=1..60`, and use `+south` for southern false northing. Bare projection strings default to GRS80, not WGS 84, so name the ellipsoid when the distinction matters.

```text
+proj=utm +zone=32 +ellps=WGS84 +algo=auto
+proj=utm +zone=59 +south +ellps=WGS84 +algo=poder_engsager
```

## Sixth-order Krüger forward conversion

Use the third flattening `n=f/(2-f)` and a conformal-sphere step rather than the short Snyder power series. For zone `z`, use `lambda0=radians(6*z-183)`, `k0=0.9996`; angles are radians and ellipsoid axes are metres.

```text
e = sqrt(f*(2-f)); n = f/(2-f)
A = a/(1+n) * (1 + n²/4 + n⁴/64 + n⁶/256)
alpha[1..6] = [
  n/2 - 2*n²/3 + 5*n³/16 + 41*n⁴/180 - 127*n⁵/288 + 7891*n⁶/37800,
  13*n²/48 - 3*n³/5 + 557*n⁴/1440 + 281*n⁵/630 - 1983433*n⁶/1935360,
  61*n³/240 - 103*n⁴/140 + 15061*n⁵/26880 + 167603*n⁶/181440,
  49561*n⁴/161280 - 179*n⁵/168 + 6601661*n⁶/7257600,
  34729*n⁵/80640 - 3418889*n⁶/1995840,
  212378941*n⁶/319334400,
]
tau = tan(phi)
sigma = sinh(e*atanh(e*tau/sqrt(1+tau²)))
tauP = tau*sqrt(1+sigma²) - sigma*sqrt(1+tau²)
dl = lambda-lambda0
xiP = atan2(tauP, cos(dl))
etaP = asinh(sin(dl) / sqrt(tauP²+cos(dl)²))
xi = xiP + sum(alpha[j]*sin(2*j*xiP)*cosh(2*j*etaP), j=1..6)
eta = etaP + sum(alpha[j]*cos(2*j*xiP)*sinh(2*j*etaP), j=1..6)
E = 500000 + k0*A*eta
N = k0*A*xi + (phi < 0 ? 10000000 : 0)
```

The same series directly supplies meridian convergence `gamma`, grid north clockwise from true north, and point scale `k`. Both matter for ground-to-grid work. Ground distance also needs elevation reduction; projection scale alone is insufficient.

```text
p = 1 + sum(2*j*alpha[j]*cos(2*j*xiP)*cosh(2*j*etaP), j=1..6)
q =     sum(2*j*alpha[j]*sin(2*j*xiP)*sinh(2*j*etaP), j=1..6)
gamma = atan(tauP/sqrt(1+tauP²)*tan(dl)) + atan2(q, p)
k = k0 * sqrt(1-e²*sin(phi)²) * sqrt(1+tau²)
    / sqrt(tauP²+cos(dl)²) * (A/a) * sqrt(p²+q²)
```

## Sixth-order Krüger inverse conversion

Remove false origins, apply the distinct `beta` projected series, then use a short Newton solve to recover geodetic rather than conformal latitude. Supplying the wrong hemisphere changes the removed false northing by 10,000 km. Hemisphere is generally ambiguous from easting/northing alone and must travel with the coordinate.

```text
beta[1..6] = [
  n/2 - 2*n²/3 + 37*n³/96 - n⁴/360 - 81*n⁵/512 + 96199*n⁶/604800,
  n²/48 + n³/15 - 437*n⁴/1440 + 46*n⁵/105 - 1118711*n⁶/3870720,
  17*n³/480 - 37*n⁴/840 - 209*n⁵/4480 + 5569*n⁶/90720,
  4397*n⁴/161280 - 11*n⁵/504 - 830251*n⁶/7257600,
  4583*n⁵/161280 - 108847*n⁶/3991680,
  20648693*n⁶/638668800,
]
eta = (E-500000)/(k0*A)
xi = (N-(hemisphere == 'S' ? 10000000 : 0))/(k0*A)
xiP = xi - sum(beta[j]*sin(2*j*xi)*cosh(2*j*eta), j=1..6)
etaP = eta - sum(beta[j]*cos(2*j*xi)*sinh(2*j*eta), j=1..6)
tauP = sin(xiP) / sqrt(sinh(etaP)²+cos(xiP)²)
tau = tauP
repeat:
  sigma = sinh(e*atanh(e*tau/sqrt(1+tau²)))
  trial = tau*sqrt(1+sigma²) - sigma*sqrt(1+tau²)
  dtau = (tauP-trial)/sqrt(1+trial²)
       * (1+(1-e²)*tau²) / ((1-e²)*sqrt(1+tau²))
  tau += dtau
until abs(dtau) <= 1e-12
phi = atan(tau)
lambda = lambda0 + atan2(sinh(etaP), cos(xiP))
```

## Movable Type UTM behavior

`LatLon.toUtm(zoneOverride)` can deliberately project a point in a neighboring zone. Extended-zone coordinates can have unusual or negative eastings, and the override interacts with Norway/Svalbard exception logic. The `Utm` constructor normally range-checks conventional eastings and northings; pass `verifyEN=false` as its final argument for coherent extended coordinates or alternative-datum ranges.

Forward results carry `utm.convergence` and `utm.scale`. `Utm.toLatLon()` attaches the same properties to the returned point.

```js
import Utm, { LatLon } from 'geodesy/utm.js';

const extended = new LatLon(48.8582, 2.2945).toUtm(32);
console.log(extended.convergence, extended.scale);

const point = Utm.parse('31 N 448251 5411932').toLatLon();
console.log(point.convergence, point.scale);
```

## MGRS cells and formatting

An MGRS reference identifies a square, not a point. `Mgrs.toUtm()` returns the square’s south-west corner. `Mgrs.parse()` right-pads shorter easting and northing components with zeros, so `31U DQ 48 11` converts to corner `31 N 448000 5411000`, not its centre.

`Mgrs.toString(digits)` truncates easting and northing to the requested precision; `Utm.toString(digits)` rounds them. MGRS output has no space inside the zone/band designator but spaces between components. Produce compact military text with `mgrs.toString().replace(/ /g, '')`.

## South African Lo coordinates

Hartebeesthoek94 Lo uses `yWesting` and `xSouthing`, so signs and axis order differ from conventional easting/northing. East of the central meridian gives a negative westing; southern latitudes give positive southings.

The source implementation selects odd-degree central meridians with truncation toward zero and uses an unscaled, un-offset series rather than UTM scale and false coordinates:

```text
L0 = lon == 0 ? 1 : 2*trunc(lon/2) + sign(lon)   # degrees
l = radians(lon - L0)
```

## OS grid references

`OsGridRef.toLatLon()` interprets the grid in OSGB36 but returns WGS 84 by default; request OSGB36 explicitly when required. The returned coordinate is the south-west corner of the represented grid square, not its centre.

`OsGridRef.parse()` accepts spaced or unspaced two- through ten-digit references and comma-separated numeric metre coordinates.

```js
import OsGridRef from 'geodesy/osgridref.js';

const southwestWgs84 = OsGridRef.parse('SU 387 148').toLatLon();
```
