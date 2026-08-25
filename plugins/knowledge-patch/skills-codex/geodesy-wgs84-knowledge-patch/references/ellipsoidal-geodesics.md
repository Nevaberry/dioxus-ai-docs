# Ellipsoidal Geodesics

## Contents

- [Choose spherical or ellipsoidal calculations](#choose-spherical-or-ellipsoidal-calculations)
- [GeographicLib algorithms and tools](#geographiclib-algorithms-and-tools)
- [Vincenty shared series](#vincenty-shared-series)
- [Vincenty inverse](#vincenty-inverse)
- [Vincenty direct](#vincenty-direct)
- [Vincenty convergence and degeneracies](#vincenty-convergence-and-degeneracies)
- [Spherical path and polygon caveats](#spherical-path-and-polygon-caveats)

## Choose spherical or ellipsoidal calculations

`LatLonSpherical` uses one Earth radius and ignores ellipsoidal effects. Error is generally below `0.3%` but can reach about `0.55%` on equator-crossing routes. Its default mean radius is `6371 km`. For metre-level accuracy, use an ellipsoidal solver; the documented Vincenty alternative targets results within `1 mm`.

Spherical rhumb code uses `psi = asinh(tan(phi))`. Ellipsoidal Mercator isometric latitude must include eccentricity `e`:

```text
psi = asinh(tan(phi)) - e*atanh(e*sin(phi))
    = ln(tan(pi/4 + phi/2) * ((1-e*sin(phi))/(1+e*sin(phi)))^(e/2))
```

Rhumb distance, bearing, destination, and midpoint implementations that omit this correction remain spherical even when their inputs are geodetic latitudes.

## GeographicLib algorithms and tools

The published GeographicLib geodesic algorithm uses sixth-order series, with separate material for tenth- and thirtieth-order expansions. `GeodesicExact` and `GeodesicLineExact` are distinct elliptic-integral implementations for direct/inverse calculations and repeated points along a geodesic. Exact evaluation is not an option implied by the ordinary `Geodesic` class name.

GeographicLib also provides ellipsoidal `AzimuthalEquidistant`, `CassiniSoldner`, and `Gnomonic` projection classes and the `GeodesicProj` command-line tool. `GeodSolve` handles direct and inverse geodesics; `Planimeter` measures areas of geodesic polygons.

## Vincenty shared series

Vincenty maps geodetic latitude `phi` to auxiliary-sphere reduced latitude `U`. Direct and inverse solutions share the following series. Angles are radians; distance has the same unit as ellipsoid axes `a` and `b`.

```text
U = atan((1-f)*tan(phi))
u2 = cos2Alpha * (a*a-b*b)/(b*b)
A = 1 + u2/16384*(4096 + u2*(-768 + u2*(320-175*u2)))
B = u2/1024*(256 + u2*(-128 + u2*(74-47*u2)))
q = cos(2*sigmaM)
deltaSigma = B*sinSigma*(q + B/4*(cosSigma*(-1+2*q*q)
             - B*q/6*(-3+4*sinSigma*sinSigma)*(-3+4*q*q)))
```

Vincenty’s 1976 replacement coefficients use Helmert’s expansion parameter and can replace the original `A/B` polynomials wherever the shared coefficients are evaluated:

```text
k1 = (sqrt(1+u2)-1)/(sqrt(1+u2)+1)
A = (1+k1*k1/4)/(1-k1)
B = k1*(1-3*k1*k1/8)
```

## Vincenty inverse

For two points, set `L=lambda2-lambda1`, compute `U1/U2`, and initialize the auxiliary-sphere longitude `lambda=L`. Iterate the recurrence below. Use `atan2(sinSigma, cosSigma)`, not a one-argument arctangent, to preserve the quadrant and accuracy near poles and the equator.

```text
sinSigma = hypot(cosU2*sin(lambda),
                 cosU1*sinU2 - sinU1*cosU2*cos(lambda))
cosSigma = sinU1*sinU2 + cosU1*cosU2*cos(lambda)
sigma = atan2(sinSigma, cosSigma)
sinAlpha = cosU1*cosU2*sin(lambda)/sinSigma
cos2Alpha = 1-sinAlpha*sinAlpha
q = cosSigma - 2*sinU1*sinU2/cos2Alpha
C = f*cos2Alpha*(4 + f*(4-3*cos2Alpha))/16
lambda = L + (1-C)*f*sinAlpha*(sigma + C*sinSigma*(q
         + C*cosSigma*(-1+2*q*q)))
```

Stop when the change in `lambda` is at most `1e-12` radians. Then evaluate the shared `u2/A/B/deltaSigma` series and outputs:

```text
s = b*A*(sigma-deltaSigma)
alpha1 = atan2(cosU2*sin(lambda), cosU1*sinU2-sinU1*cosU2*cos(lambda))
alpha2 = atan2(cosU1*sin(lambda), -sinU1*cosU2+cosU1*sinU2*cos(lambda))
```

`alpha2` is the forward azimuth at point 2 while continuing in the point-1-to-point-2 direction. Normalize both azimuths to the caller’s bearing range, commonly `[0, 2*pi)`.

## Vincenty direct

Given point 1, initial azimuth `alpha1`, and ellipsoidal distance `s`, derive the equatorial azimuth and initialize `sigma=s/(b*A)`. Iterate `sigma`, then recover the destination longitude correction and final forward azimuth.

```text
sigma1 = atan2(tanU1, cos(alpha1))
sinAlpha = cosU1*sin(alpha1); cos2Alpha = 1-sinAlpha*sinAlpha
u2, A, B = shared_series(cos2Alpha)
sigma = s/(b*A)
repeat:
    q = cos(2*sigma1 + sigma)
    deltaSigma = shared_delta(B, sin(sigma), cos(sigma), q)
    sigma = s/(b*A) + deltaSigma
until change(sigma) <= 1e-12
x = sinU1*sin(sigma) - cosU1*cos(sigma)*cos(alpha1)
phi2 = atan2(sinU1*cos(sigma)+cosU1*sin(sigma)*cos(alpha1),
             (1-f)*hypot(sinAlpha, x))
lambdaAux = atan2(sin(sigma)*sin(alpha1),
                  cosU1*cos(sigma)-sinU1*sin(sigma)*cos(alpha1))
C = f*cos2Alpha*(4 + f*(4-3*cos2Alpha))/16
L = lambdaAux - (1-C)*f*sinAlpha*(sigma + C*sin(sigma)*(q
    + C*cos(sigma)*(-1+2*q*q)))
lambda2 = lambda1 + L; alpha2 = atan2(sinAlpha, -x)
```

## Vincenty convergence and degeneracies

### Coincident, antipodal, and equatorial cases

If `sinSigma` is zero, `sinAlpha` is indeterminate and the points may be coincident or exactly opposite. Distinguish them before dividing:

- A coincident pair has zero distance and undefined bearings.
- An exact antipode has no unique geodesic or azimuth.

On an equatorial geodesic, `cos2Alpha` is zero. Avoid the division used to form `q`. `C` is also zero, so `q` is unused; a finite sentinel such as `0` is safe, while the equatorial limiting value is `-1`.

### Nearly antipodal inverse failure

The ordinary inverse iteration can become slow, fail, or return a bad result near an antipode. On WGS 84, the cited implementation observed trouble above roughly `19,936 km`, within about `75 km` of the antipodal point. Always bound and verify convergence, then fall back to a globally convergent inverse solver instead of returning the last iterate.

Regression cases:

- `(0°,0°)` to `(0.5°,179.5°)` needs about 130 iterations for `19,936,288.579 m`.
- `(0°,0°)` to `(0.5°,179.7°)` makes the ordinary recurrence fail.

A 100-iteration cap can reject a valid slow case; merely raising the cap does not solve the failure region.

### Movable Type wrapper semantics

`latlon-ellipsoidal-vincenty.js` defaults to WGS 84 and selects an alternative ellipsoid only from the source point’s `datum`. Both points must already share a datum and must have zero height because these are ellipsoid-surface, not 3D or terrain, distances.

`distanceTo()`, `initialBearingTo()`, and `finalBearingTo()` convert inverse-convergence errors to `NaN` and round to `0.001 m` or seven decimal degrees. Direct and intermediate operations can propagate convergence errors. Handle both failure forms.

## Spherical path and polygon caveats

### Bearing-defined intersections

For the spherical-trigonometry construction:

```text
alpha1 = theta13 - theta12
alpha2 = theta21 - theta23
```

There are infinitely many solutions when both `sin(alpha1)` and `sin(alpha2)` are zero, and an ambiguous antipodal/360-degree solution when their product is negative. The implementation returns no unique point in either case. It can also be ill-conditioned for meridional or equatorial paths; do not assume every two start-point/bearing pairs yield one usable intersection.

### Pole-crossing polygon area

`LatLonSpherical.areaOf()` computes an area bounded by great-circle arcs and applies a special spherical-excess correction when its course-delta heuristic indicates an enclosed pole. That heuristic has an intermittent recorded failure for pole-crossing edges, including `(85,90), (85,0), (85,-90)`. Do not use it for such polygons without an independent pole-enclosure check.
