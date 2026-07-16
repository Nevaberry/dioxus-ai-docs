# Helmert and Datum Transformations

## Contents

- [PROJ Helmert operations](#proj-helmert-operations)
- [NGS same-epoch frame transformations](#ngs-same-epoch-frame-transformations)
- [Molodensky and Molodensky-Badekas](#molodensky-and-molodensky-badekas)
- [Multiple-regression transformations](#multiple-regression-transformations)

## PROJ Helmert operations

### Coordinate domain and units

`+proj=helmert` operates on Cartesian coordinates. For a 3D geographic workflow, convert longitude, latitude, and ellipsoidal height to geocentric coordinates before the Helmert step and convert back afterward.

The 3D form uses:

- `x/y/z` in metres.
- `rx/ry/rz` in arcseconds.
- `s` in ppm.

The 2D form instead uses `x/y` in metres, `theta` in arcseconds, and a unitless `s`:

```text
+proj=helmert +x=-9597.3572 +y=0.6112 +s=0.304794780637 +theta=-1.244048
```

### Kinematic parameters and coordinate epoch

Adding any rate makes the operation kinematic. PROJ uses `dx/dy/dz` in m/year, `drx/dry/drz` in arcseconds/year, and `ds` in ppm/year. It evaluates every parameter as:

```text
P(t) = P(t_epoch) + dP * (t - t_epoch)
```

Both `t_epoch` and the observation time supplied as the coordinate’s fourth component are decimal years.

```text
+proj=helmert +convention=position_vector \
  +x=0.0127 +y=0.0065 +z=-0.0209 +s=0.00195 \
  +dx=-0.0029 +dy=-0.0002 +dz=-0.0006 +ds=0.00001 \
  +rx=-0.00039 +ry=0.00080 +rz=-0.00114 \
  +drx=-0.00011 +dry=-0.00019 +drz=0.00007 +t_epoch=1988.0
```

### Rotation conventions and equations

Whenever a 3D rotation or rotation rate is present, set one of these conventions:

- `convention=coordinate_frame`: EPSG 1032 for geocentric or EPSG 9607 for geographic coordinates.
- `convention=position_vector`: EPSG 1033 for geocentric or EPSG 9606 for geographic coordinates.

Negating every rotation and rotation-rate parameter changes between the conventions. It does not reverse source and target; invert the operation itself to reverse direction. Add `+exact` when full rotation equations are required instead of the default small-angle approximation. The old `transpose` switch is forbidden from PROJ 5.2 onward.

## NGS same-epoch frame transformations

Historical NGS parameters transform ITRF or IGS coordinates to the named NAD83 realization at the same coordinate epoch. They do not propagate a station to a different epoch. HTDP combines frame transformations with crustal-motion models; a bare Helmert operation is generally wrong when input and output epochs differ unless an appropriate velocity or motion model is applied separately.

NGS uses translations `T` in metres, rotations `e` in milliarcseconds, and scale in ppb, all propagated from `t0`. Convert rotations with `4.84813681e-9 rad/mas` and scale with `1e-9` per ppb. Its coordinate-frame equations are:

```text
Xn = Tx + (1+s)Xi + ez*Yi - ey*Zi
Yn = Ty - ez*Xi + (1+s)Yi + ex*Zi
Zn = Tz + ey*Xi - ex*Yi + (1+s)Zi
```

### IGS08 to NAD83(2011), PA11, and MA11

These parameters have `t0=1997.0` and are in the explicit IGS08-to-NAD83 direction. NGS ended support for the set on 27 January 2017. Vectors are ordered `(x,y,z)` and retain NGS native units.

| Target | `T` (m) | `e` (mas) | `s` (ppb) | `dT` (m/yr) | `de` (mas/yr) | `ds` (ppb/yr) |
| --- | --- | --- | ---: | --- | --- | ---: |
| NAD83(2011) | `(0.99343, -1.90331, -0.52655)` | `(25.91467, 9.42645, 11.59935)` | `1.71504` | `(0.00079, -0.00060, -0.00134)` | `(0.06667, -0.75744, -0.05133)` | `-0.10201` |
| NAD83(PA11) | `(0.9080, -2.0161, -0.5653)` | `(27.741, 13.469, 2.712)` | `1.10` | `(0.0001, 0.0001, -0.0018)` | `(-0.384, 1.007, -2.186)` | `0.08` |
| NAD83(MA11) | `(0.9080, -2.0161, -0.5653)` | `(28.971, 10.420, 8.928)` | `1.10` | `(0.0001, 0.0001, -0.0018)` | `(-0.020, 0.105, -0.347)` | `0.08` |

For PROJ, divide `e/de` and `s/ds` by 1000 to obtain arcseconds and ppm, then use `+convention=coordinate_frame`. This still performs only the same-epoch frame transformation, not HTDP crustal motion.

### Older ITRF-to-NAD83 sets

These ended-support transformations are in the stated source-to-target direction. ITRF2000, ITRF97, and ITRF96 use `t0=1997.0`; ITRF94 uses `1996.0`; ITRF93 uses `1995.0`.

| Source to target | `T` (m) | `e` (mas) | `s` (ppb) | `dT` (m/yr) | `de` (mas/yr) | `ds` (ppb/yr) |
| --- | --- | --- | ---: | --- | --- | ---: |
| ITRF2000 to NAD83(CORS96) | `(0.99563, -1.90131, -0.52145)` | `(25.91467, 9.42645, 11.59935)` | `0.61504` | `(0.00069, -0.00070, 0.00046)` | `(0.06667, -0.75744, -0.05133)` | `-0.18201` |
| ITRF2000 to NAD83(PACP00) | `(0.9102, -2.0141, -0.5602)` | `(27.741, 13.469, 2.712)` | `0` | `(0, 0, 0)` | `(-0.384, 1.007, -2.186)` | `0` |
| ITRF2000 to NAD83(MARP00) | `(0.9102, -2.0141, -0.5602)` | `(28.971, 10.420, 8.928)` | `0` | `(0, 0, 0)` | `(-0.020, 0.105, -0.347)` | `0` |
| ITRF97 to NAD83(CORS96) | `(0.98893, -1.90741, -0.50295)` | `(25.91467, 9.42645, 11.59935)` | `-0.93496` | `(0.00069, -0.00010, 0.00186)` | `(0.06667, -0.75744, -0.03133)` | `-0.19201` |
| ITRF96 to NAD83(CORS96) | `(0.9910, -1.9072, -0.5129)` | `(25.79, 9.65, 11.66)` | `0` | `(0, 0, 0)` | `(0.0532, -0.7423, -0.0316)` | `0` |
| ITRF94 to NAD83(CORS94) | `(0.9738, -1.9453, -0.5486)` | `(27.55, 10.05, 11.36)` | `0` | `(0, 0, 0)` | `(0.09, -0.77, 0.02)` | `0` |
| ITRF93 to NAD83(CORS93) | `(0.9769, -1.9392, -0.5461)` | `(26.40, 10.10, 10.30)` | `0` | `(0, 0, 0)` | `(0, 0, 0)` | `0` |

NGS ended support for the ITRF2000 sets in 2011, ITRF97 in 2002, ITRF96 in 2000, ITRF94 in 1998, and ITRF93 in 1996. The ITRF97 set is an adopted composition through ITRF96. The ITRF94 and ITRF93 sets predate, and are not consistent with, the relationships encoded in HTDP.

## Molodensky and Molodensky-Badekas

The Molodensky transformation shifts geodetic `(phi, lambda, h)` directly using three datum-centre translations plus source-to-target ellipsoid differences `delta_a` and `delta_f`; it has no intermediate ECEF step.

Molodensky-Badekas is a ten-parameter ECEF similarity transformation whose three extra parameters define a source-datum pivot near the fitted region, reducing translation/rotation coupling:

```text
q = P_A - C_A
P_B = P_A + T + Omega*q + delta_s*q
Omega = [[0,-rz,ry], [rz,0,-rx], [-ry,rx,0]]
```

These signs are the small-angle position-vector form. Because `C_A` is tied to the source datum, do not reverse the transformation merely by negating translation, rotation, and scale. Use parameters and a pivot defined for the reverse direction.

## Multiple-regression transformations

Legacy MRE transformations map geodetic coordinates directly, without ECEF, using region-fitted polynomials that may extend to ninth degree. Normalize around the model’s stated datum origin and scale, apply separately fitted equations for `delta_phi`, `delta_lambda`, and `delta_h`, and do not extrapolate outside the fitted region.

```text
U = K*(phi_A - phi_m)
V = K*(lambda_A - lambda_m)
delta_phi = a0 + a1*U + a2*V + a3*U^2 + a4*U*V + a5*V^2 + ...
```
