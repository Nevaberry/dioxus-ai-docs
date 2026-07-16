# Atmospheric and Multipath Error Modeling

## Ionospheric combinations and residuals

### PPP ionosphere-free clock and group-delay convention

For code or carrier observables in metres, `X_IF = (f1² X1 - f2² X2) / (f1² - f2²)` removes more than 99.9% of the first-order ionospheric term. When the satellite clock used by PPP is referenced to this ionosphere-free code combination, Timing Group Delays cancel in the combination and must not be applied separately.

### Residual second-order ionosphere

The geomagnetic second-order term left after first-order ionosphere removal is `I2_phase,f = -(7527 c / (2 f³)) ∫ Ne B cos(θ) dl`, with `I2_group,f = -2 I2_phase,f`. In global geodetic processing it mainly affects clock estimates at centimetre level and orbits at millimetre level, while its static receiver-position effect is normally below one millimetre.

## Tropospheric state modeling

### Hydrostatic and wet troposphere states

Tropospheric delay is effectively non-dispersive at GNSS frequencies, so it affects code and carrier equally and cannot be eliminated with a dual-frequency combination. Roughly 90% is predictable hydrostatic delay—about 2.3 m at zenith and 10 m at 10 degrees elevation—whereas the wet component is only tens of centimetres but changes rapidly enough that precise filters normally estimate it with the coordinates.

### SBAS troposphere mapping and seasonal phase

The SBAS-adopted Collins model applies one mapping to both zenith components, `T(E) = (Tz,dry + Tz,wet) * 1.001 / sqrt(0.002001 + sin²(E))`; this mapping is valid only above 5 degrees elevation. Its pressure, temperature, water-vapour pressure, temperature-lapse, and water-vapour-lapse climatology uses `xi(phi,D) = xi0(phi) - delta_xi(phi) cos(2π(D-Dmin)/365.25)`, with `Dmin = 28` north of the equator and `211` south, latitude interpolation, and receiver height above mean sea level.

### PPP wet-delay state example

A PPP model can use separate Niell wet and dry mappings with `Tz,dry = 2.3 exp(-0.116e-3 H)` metres and `Tz,wet = 0.1 m + delta_Tz,wet`, where `H` is height above mean sea level. Estimate `delta_Tz,wet` in the navigation filter as a random walk alongside position; the documented example uses process noise of about `1 cm²/h`.

## Multipath bounds and diagnostics

### Code and carrier multipath limits

Code multipath has a theoretical limit of 1.5 code-chip lengths—about 450 m for GPS C1, though values above 15 m are difficult to observe and 2–3 m is typical—while carrier multipath is bounded by one quarter wavelength, about 5 cm on GPS L1/L2 and typically below 1 cm. Long-delay reflections are primarily a receiver-processing problem, whereas short-delay rejection depends primarily on the antenna.

### Sidereal-repeat multipath diagnostic

For a static GPS antenna, satellite-reflector geometry and its multipath signature repeat by sidereal rather than solar day, so align consecutive daily traces earlier by about 236 seconds per day. A code-minus-carrier trace follows `R1 - Phi1 = 2 alpha1 I + bias + multipath + noise`, so its repeating component reveals multipath while its slow drift still contains ionospheric refraction.
