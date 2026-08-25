# Cartesian and Local Coordinates

## ECEF to geodetic with Olson’s closed form

Olson’s inverse computes geodetic latitude and ellipsoidal height without iteration. It switches between sine- and cosine-based latitude estimates at `c2 = 0.3` to stay well conditioned near the equator and poles. It also avoids the pole-singular compact Bowring height expression `p / cos(phi) - N`.

Reject the Earth-centre input where `r = 0`. Define an application policy for longitude when `X = Y = 0`, because longitude is then indeterminate.

```text
a1=a*e2; a2=a1*a1; a3=a1*e2/2; a4=2.5*a2; a5=a1+a3; a6=1-e2
za=abs(Z); w=hypot(X,Y); r=hypot(w,Z); s2=Z*Z/(r*r); c2=w*w/(r*r)
u=a2/r; v=a3-a4/r
if c2 > 0.3:
    s=(za/r)*(1+c2*(a1+u+s2*v)/r); phi=asin(s); c=sqrt(1-s*s)
else:
    c=(w/r)*(1-s2*(a5-u-c2*v)/r); phi=acos(c); s=sqrt(1-c*c)
g=1-e2*s*s; rg=a/sqrt(g); rf=a6*rg
u=w-rg*c; v=za-rf*s; f=c*u+s*v; m=c*v-s*u
p=m/(rf/g+f)
phi=copySign(phi+p,Z); lambda=atan2(Y,X); h=f+m*p/2
```

## Fixed-origin ENU for ECEF odometry

`FP_A-LLH` uses the WGS 84 geodetic datum. `FP_A-ODOMETRY` supplies pose in ECEF; its orientation is body-to-ECEF and uses the scalar-first unit-quaternion convention `[w, εx, εy, εz]`.

To keep position, velocity, and orientation in one stable local frame, select one origin `(φ0, λ0, h0)` and reuse its `R_ecef^enu0`. Do not rebuild the basis at every current position.

```text
p_body^enu0 = R_ecef^enu0 (p_body^ecef - p_enu0^ecef)
v_body^enu0 = R_ecef^enu0 v_body^ecef
R_body^enu0 = R_ecef^enu0 R_body^ecef
```

## PROJ topocentric operations

In the forward direction, `+proj=topocentric` maps geocentric `(X,Y,Z)` metres to local `(East,North,Up)`. Define its origin with exactly one of:

- Geocentric `X_0/Y_0/Z_0` in metres.
- Geographic `lon_0/lat_0` in degrees plus ellipsoidal `h_0` in metres.

Geographic input must first pass through `+proj=cart`. This composition is EPSG method 9837; standalone geocentric-to-topocentric is EPSG method 9836.

The operation defaults to GRS80 and `h_0=0`. State WGS 84 explicitly when required:

```text
+proj=pipeline +ellps=WGS84
+step +proj=cart
+step +proj=topocentric +lon_0=5 +lat_0=55 +h_0=200
```
