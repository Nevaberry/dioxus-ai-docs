# Coordinate Conversions

## Olson's Closed-Form ECEF → Geodetic

Non-iterative, ~3 nm accuracy. Avoids the iterative Bowring method and handles polar/equatorial edge cases through the `c2 > 0.3` branch selection.

Key constants for WGS84:

```java
a  = 6378137.0;              e2 = 6.6943799901377997e-3;
a1 = 4.2697672707157535e+4;  a2 = 1.8230912546075455e+9;
a3 = 1.4291722289812413e+2;  a4 = 4.5577281365188637e+9;
a5 = 4.2840589930055659e+4;  a6 = 9.9330562000986220e-1;

lon = atan2(y, x);
zp = abs(z); w2 = x*x + y*y; w = sqrt(w2);
r2 = w2 + z*z; r = sqrt(r2);
s2 = z*z/r2; c2 = w2/r2; u = a2/r; v = a3 - a4/r;
if (c2 > 0.3) { s = (zp/r)*(1 + c2*(a1+u+s2*v)/r); lat = asin(s); ss=s*s; c=sqrt(1-ss); }
else           { c = (w/r)*(1 - s2*(a5-u-c2*v)/r); lat = acos(c); ss=1-c*c; s=sqrt(ss); }
g = 1-e2*ss; rg = a/sqrt(g); rf = a6*rg;
u = w-rg*c; v = zp-rf*s; f = c*u+s*v; m = c*v-s*u; p = m/(rf/g+f);
lat += p; alt = f + m*p/2;
if (z < 0) lat = -lat;
```

## ECEF ↔ ENU Rotation Matrix

The rotation from ECEF difference vector to ENU (φ=latitude, λ=longitude):

```
      ┌ -sin(λ)            cos(λ)           0      ┐
R  =  │ -cos(λ)·sin(φ)    -sin(λ)·sin(φ)   cos(φ) │
      └  cos(λ)·cos(φ)     sin(λ)·cos(φ)   sin(φ) ┘

[E, N, U]ᵀ = R · [Δx, Δy, Δz]ᵀ    where Δ = point_ECEF - ref_ECEF
```

- ENU→ECEF uses transpose Rᵀ
- For NED, swap rows: row1→N(row2), row2→E(row1), row3→-U
