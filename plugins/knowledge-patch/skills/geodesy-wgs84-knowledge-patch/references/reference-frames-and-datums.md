# Reference Frames and Datums

## Contents

- [WGS 84](#wgs-84)
- [ITRF2020](#itrf2020)
- [ETRS89](#etrs89)
- [Broadcast GNSS frames](#broadcast-gnss-frames)

## WGS 84

### Current realization

WGS 84 (G2296) became the current WGS 84 reference frame on 7 January 2024, superseding G2139. It is aligned to ITRF2020 and the IGS20 frame. Name G2296 explicitly for precision-sensitive data and transformations instead of treating an unspecified “WGS 84” as a timeless realization.

### Relationship to ITRF

The operational WGS 84 frame is realized by Cartesian antenna-reference-point coordinates at GPS monitor stations and is aligned to ITRF within one centimetre in each 3D component. Its seven-parameter frame transformation to ITRF is zero in every component by design. Do not add a Helmert transformation merely to convert between the aligned frames.

### Gravitational constants

The WGS 84 defining geocentric gravitational constant, including the atmosphere, is `3.986004418e14 m³/s²`. The value specified for GPS users is `3.9860050e14 m³/s²`. Keep the convention explicit in precision orbit or dynamics code rather than silently substituting one for the other.

## ITRF2020

### ITRF2020-u2024 preserves the datum

`ITRF2020-u2024` is the second regular update. Despite the `u2024` label, it extends the four space-geodesy input series through 2025.0. It retains the ITRF2020 origin, scale, and orientation through no-net constraints, so every transformation parameter between ITRF2020-u2024 and ITRF2020 is zero. Treat it as updated station and motion data, not a datum change.

For high-precision epoch propagation, use the u2024 long-term positions and velocities together with its separate discontinuity, post-seismic-deformation, and annual/semi-annual station-motion products. The `.SNX.gz` product carries covariance; `.SSC` does not. The ITRF2020 seasonal geocenter-motion model was not updated for u2024.

### Frame definition

At epoch 2015.0:

- The long-term origin has zero translations and zero translation rates relative to the ILRS SLR frame over 1993.0–2021.0.
- Scale and scale rate are tied to the average of selected VLBI sessions through 2013.75 and SLR weeks over 1997.7–2021.0.
- Orientation has zero rotations and zero rotation rates relative to ITRF2014.

### ITRF2020 to ITRF2014

At epoch 2015.0, the published direction is explicitly `ITRF2014 minus ITRF2020`:

```text
T  = (-1.4, -0.9, +1.4) mm
D  = -0.42 ppb
R  = (0, 0, 0) mas
dT = (0.0, -0.1, +0.2) mm/yr
dD = 0 ppb/yr
dR = (0, 0, 0) mas/yr
```

Preserve that direction when applying or inverting the transformation.

### Plate motion and Earth orientation

The ITRF2020 plate-motion model fits 13 plate rotation poles plus an Origin Rate Bias. Add that bias to pole-predicted horizontal velocities for consistency with ITRF2020, but discard the vertical velocity produced by adding it.

The initially published ITRF2020 UT1 and length-of-day values contained a zonal-tide sign error of a few tenths of a millisecond. `ITRF2020_EOP-F1.DAT` and `ITRF2020_EOP-F2.DAT` were corrected on 9 August 2023. Replace copies downloaded earlier.

## ETRS89

ETRS89 was coincident with ITRS at epoch 1989.0 and is fixed to stable Eurasia. `89` is the definition epoch, not a realization name, and transformations to ITRS are time-dependent.

Select the CRS at the required realization and dimensional accuracy:

| CRS | Meaning |
| --- | --- |
| `EPSG:4258` | 2D ETRS89 ensemble, 0.1 m |
| `EPSG:4937` | 3D ETRS89 ensemble, 0.1 m |
| `EPSG:9067` | 2D ETRF2000 realization |
| `EPSG:7931` | 3D ETRF2000 realization |
| `EPSG:9423` | Compound ETRS89 2D plus mean-tide EVRF2019 height |

## Broadcast GNSS frames

### GPS

GPS broadcast ephemerides reference the satellite antenna phase centre in WGS 84. A receiver position solved from them is expressed in the same ECEF frame. Do not generalize this convention to every GNSS.

### GLONASS and PZ-90.11

GLONASS has broadcast in PZ-90.11 since 31 December 2013. Its published conversion to ITRF2008 has no rotation or scale, only this origin shift, with `0.002 m` uncertainty per component:

```text
[X, Y, Z]ITRF2008 = [X, Y, Z]PZ-90.11 + [0.003, 0.001, 0.001] m
```

### Galileo and GTRF

GTRF is an independent ITRS realization derived from Galileo Sensor Station coordinates and aligned using selected IGS stations. At the ITRF markers used to realize GTRF, its coordinates must remain within `3 cm (2σ)` of the latest ITRF. GTRF is realigned when new ITRF realizations appear, so use transformation parameters valid for the particular GTRF realization.

### BeiDou and BDC

BeiDou navigation data uses BDC, which is consistent with CGCS2000 and referred to ITRF97 at epoch 2000.0. Its ellipsoid takes `a`, `J2`, and Earth angular velocity from GRS80, the gravitational constant from WGS 84, and flattening `f = 1/298.257222101`. Preserve that combination rather than substituting a generic WGS 84 ellipsoid.
