# Library-Specific Behavior

## GeographicLib package scope

GeographicLib C++ 2.5 covers:

- Geodesic and rhumb calculations.
- Geographic, UTM, UPS, MGRS, geocentric, and local-Cartesian conversions.
- Gravity and geomagnetic models.
- Triaxial-ellipsoid calculations.

The GeographicLib Python 2.1 package implements only the geodesic portion: `geodesic`, `geodesicline`, `polygonarea`, and `constants`. Do not assume the Python package mirrors the C++ feature surface.

## Movable Type ellipsoidal modules

The base `latlon-ellipsoidal.js` module defines only the WGS 84 ellipsoid and datum and provides no datum transformations. Its `height` is metres above the ellipsoid. Historical datum transforms and modern time-dependent reference-frame transforms use separate ES-module entry points.

```js
import LatLon from 'geodesy/latlon-ellipsoidal.js';
import LatLonDatum from 'geodesy/latlon-ellipsoidal-datum.js';
import LatLonFrame from 'geodesy/latlon-ellipsoidal-referenceframe.js';
```

### Historical datum conversions

`LatLonDatum.datums` associates each historical datum with an ellipsoid and seven-parameter Helmert values in the WGS-84-to-target direction. `convertDatum()` converts through ECEF.

The supplied datum set is deliberately limited. Do not assume any result is better than one metre; several supported datums are less accurate.

### Dynamic reference-frame conversions

`latlon-ellipsoidal-referenceframe.js` defaults to ITRF2014. If coordinate epoch is omitted, it defaults to the frame’s reference epoch; that fallback is not a substitute for the actual observation epoch.

Its limited 14-parameter set covers dynamic ITRF frames from ITRF2000 onward and conversions to static NAD83, ETRF2000, and GDA94. `convertReferenceFrame()` changes the frame while preserving the coordinate’s observation epoch.

```js
const p = new LatLonFrame(51.4778, -0.0015, 0,
    LatLonFrame.referenceFrames.ITRF2014, 2025.5);
```

## N-vector operations

### Ellipsoidal local deltas

In `latlon-nvector-ellipsoidal.js`, `point.deltaTo(other)` returns a north-east-down local vector, and `point.destinationPoint(delta)` consumes the same representation. The exported `Ned` class exposes length, bearing, and elevation and can be built with `Ned.fromDistanceBearingElevation()`.

```js
import LatLon, { Ned } from 'geodesy/latlon-nvector-ellipsoidal.js';

const start = new LatLon(51.4778, -0.0015, 0);
const end = new LatLon(51.4780, -0.0010, 10);
const delta = start.deltaTo(end);
const endAgain = start.destinationPoint(delta);
const offset = Ned.fromDistanceBearingElevation(100, 45, 10);
```

### Spherical paths

N-vector `LatLon.intersection()` accepts each path as either a start point plus bearing or a pair of points. `crossTrackDistanceTo()` likewise accepts an endpoint or bearing and returns a signed distance to the containing great circle. Use `nearestPointOnSegment()` when the finite segment, rather than the infinite great circle, is required.

## DMS formatting

`Dms.separator` defaults to U+202F NARROW NO-BREAK SPACE between degrees, minutes, seconds, and the cardinal suffix. Set it before formatting when plain spaces or compact output are required. `toBrng()` also normalizes bearings into `0°..360°`.

```js
import Dms from 'geodesy/dms.js';

Dms.separator = '';
const bearing = Dms.toBrng(-3.62, 'dms', 0); // 356°22′48″
```
