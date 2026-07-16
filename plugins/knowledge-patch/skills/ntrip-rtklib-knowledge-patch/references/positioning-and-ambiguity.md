# Positioning and Ambiguity Resolution

## Contents

- [Core positioning configuration](#core-positioning-configuration)
  - [Position-model option applicability](#position-model-option-applicability)
  - [Ambiguity controls and defaults](#ambiguity-controls-and-defaults)
  - [Base coordinates and antenna metadata](#base-coordinates-and-antenna-metadata)
  - [Configuration-file encoding](#configuration-file-encoding)
  - [Static-output and base-interpolation semantics](#static-output-and-base-interpolation-semantics)
- [Positioning models and algorithm boundaries](#positioning-models-and-algorithm-boundaries)
  - [Post-processed RTCM-SSR input](#post-processed-rtcm-ssr-input)
  - [Synchronized-solution option is a no-op](#synchronized-solution-option-is-a-no-op)
  - [RAIM FDE limits](#raim-fde-limits)
  - [Moving-baseline timing and length constraint](#moving-baseline-timing-and-length-constraint)
  - [Experimental PPP ambiguity resolution boundary](#experimental-ppp-ambiguity-resolution-boundary)
  - [IERS_MODEL changes two model families](#iersmodel-changes-two-model-families)
- [Demo5 positioning and ambiguity resolution](#demo5-positioning-and-ambiguity-resolution)
  - [Demo5 configuration-reference boundary](#demo5-configuration-reference-boundary)
  - [Static-start positioning and frequency mapping](#static-start-positioning-and-frequency-mapping)
  - [Combined filtering with or without phase reset](#combined-filtering-with-or-without-phase-reset)
  - [Multi-pass ambiguity resolution and satellite qualification](#multi-pass-ambiguity-resolution-and-satellite-qualification)
  - [Adaptive ratio and convergence gates](#adaptive-ratio-and-convergence-gates)
  - [Fix, hold, and single-satellite exclusion floors](#fix-hold-and-single-satellite-exclusion-floors)
  - [Hold feedback and sample-count units](#hold-feedback-and-sample-count-units)
  - [GLONASS inter-frequency-bias handling](#glonass-inter-frequency-bias-handling)
  - [Separate slip and innovation rejection controls](#separate-slip-and-innovation-rejection-controls)
  - [Matched real-time solution mode](#matched-real-time-solution-mode)
  - [PPP option boundary](#ppp-option-boundary)
  - [Extended observation-error model](#extended-observation-error-model)
  - [Optional velocity solution fields](#optional-velocity-solution-fields)
- [Branch-aware post-processing](#branch-aware-post-processing)
  - [Reproducing the upstream 2.4.3 branch](#reproducing-the-upstream-243-branch)
  - [Adaptive satellite admission is Demo5-only](#adaptive-satellite-admission-is-demo5-only)
  - [Outlier thresholds are branch-specific](#outlier-thresholds-are-branch-specific)
  - [Galileo E5b occupies a different frequency slot in Demo5](#galileo-e5b-occupies-a-different-frequency-slot-in-demo5)
- [Measurement and correction configuration](#measurement-and-correction-configuration)
  - [Signal-quality masks are endpoint- and frequency-specific](#signal-quality-masks-are-endpoint-and-frequency-specific)
  - [Separate elevation gates for solution, fix, and hold](#separate-elevation-gates-for-solution-fix-and-hold)
  - [Antenna phase-center switches require matching metadata](#antenna-phase-center-switches-require-matching-metadata)
  - [Receiver uncertainty and code/phase weighting are distinct](#receiver-uncertainty-and-codephase-weighting-are-distinct)
  - [Dynamics noise should describe antenna motion](#dynamics-noise-should-describe-antenna-motion)
  - [Differential age and provisional base coordinates](#differential-age-and-provisional-base-coordinates)
  - [Correction-model enum map](#correction-model-enum-map)
- [Ambiguity-resolution safeguards](#ambiguity-resolution-safeguards)
  - [Affected-build AR lock-count bug](#affected-build-ar-lock-count-bug)
  - [Fix-and-hold makes AR diagnostics self-referential](#fix-and-hold-makes-ar-diagnostics-self-referential)
  - [Fix-and-Bump availability boundary](#fix-and-bump-availability-boundary)

## Core positioning configuration

### Position-model option applicability

Receiver dynamics is effective only in DGPS/DGNSS and Kinematic modes; earth-tide correction is offered only for DGPS/DGNSS, Kinematic, and PPP; estimated STEC applies only to DGPS/DGNSS, Kinematic, and Static; and SSR ephemeris modes are RTKNAVI-only. Prefixing an excluded-satellite entry with `+`, such as `+R05`, forces that satellite into the solution even when its health flag would normally exclude it.

### Ambiguity controls and defaults

`Continuous`, `Instantaneous`, and `Fix and Hold` are distinct AR strategies; Fix-and-Hold constrains validated ambiguities only after its minimum fix count, while GLONASS `Auto calibration` estimates the receiver-pair inter-channel bias as a frequency-linear term. The documented defaults are ratio threshold `3.0`, ambiguity outage reset `5` epochs, geometry-free slip threshold `0.05 m`, maximum differential age `30 s`, GDOP and innovation rejection thresholds `30`, and minimum fixes before hold `10`.

```text
pos2-armode    =fix-and-hold
pos2-gloarmode=autocal
pos2-arthres   =3
pos2-arminfix  =10
pos2-aroutcnt  =5
pos2-slipthres =0.05
```

### Base coordinates and antenna metadata

RTKNAVI can take the base ARP from RTCM, while RTKPOST can use an averaged single solution, the RINEX approximate position, or a station-position file selected by the first four characters of the rover observation filename. A station record is `latitude longitude ellipsoidal-height station-id station-name`, `%` starts a comment, and SINEX is auto-detected; antenna type `*` instead imports type and delta from the RINEX header or RTCM antenna messages.

Satellite ANTEX data is required when applying precise ephemerides or SSR corrections, receiver PCV can come from ANTEX or NGS format, and PPP DCB input uses CODE format. Antenna E/N/U values are offsets of the ARP from the marker rather than coordinates of the phase center itself.

### Configuration-file encoding

RTKNAVI, RTKPOST, RTKRCV, and RNX2RTKP share `keyword = value` configuration files in which `#` starts either a whole-line or trailing comment. `pos1-navsys` is an additive mask—GPS `1`, SBAS `2`, GLONASS `4`, Galileo `8`, QZSS `16`, and Compass `32`—and antenna position sources use `llh`, `xyz`, `single`, `posfile`, `rinexhead`, or `rtcm` where applicable.

```text
pos1-posmode   =kinematic
pos1-frequency =l1+l2
pos1-navsys    =5          # GPS + GLONASS
ant2-postype   =rtcm
```

### Static-output and base-interpolation semantics

For Static or PPP-Static processing, `out-solstatic=all` emits every epoch whereas `single` emits one solution timestamped at the first epoch of the processing period. RTKPOST's `misc-timeinterp=on` linearly interpolates base observations to each rover epoch before double differencing; when it is off, the nearest base epoch is used.

## Positioning models and algorithm boundaries

### Post-processed RTCM-SSR input

RTKPOST recognizes a path ending in `.rtcm3` as an RTCM 3 SSR correction-message file, alongside broadcast-navigation input. Select `Broadcast+SSR APC` or `Broadcast+SSR CoM` consistently with the correction reference; other unrecognized extensions are treated as RINEX rather than probed as RTCM.

### Synchronized-solution option is a no-op

Although `pos2-syncsol` exposes a matched mode that would wait for rover and base/correction data, the manual explicitly says it is not implemented in 2.4.2. With the supported `off` behavior, RTKNAVI minimizes latency and extrapolates delayed base or correction data to rover time.

### RAIM FDE limits

The new `pos1-posopt5=on` RAIM FDE runs only after the single-point chi-square validation fails, retries the solution while excluding each visible satellite in turn, and keeps the candidate with the smallest normalized squared residual. It is designed for one bad measurement, not two or more, and needs two redundant satellites—at least six visible satellites—to return a solution.

### Moving-baseline timing and length constraint

Moving-baseline processing corrects the base position from its own reception epoch to the rover epoch using the base velocity estimated from Doppler, accounting for unsynchronized receiver clocks that can differ by about 2 ms. A known antenna separation is supplied with `pos2-baselen` and its standard deviation with `pos2-basesig`; for a very short baseline, `pos2-niter` greater than one helps the nonlinear constraint converge.

### Experimental PPP ambiguity resolution boundary

The 2.4.2 PPP-AR implementation accepts only CNES wide-lane fractional-cycle-bias and integer-recovery-clock products. It is explicitly experimental and unstable and is available only in post-processing when Integer Ambiguity Resolution is set to `PPP-AR`, not in RTKNAVI.

### `IERS_MODEL` changes two model families

The default precise-troposphere mapping is NMF and the default solid-earth-tide implementation follows IERS Conventions 1996. Building with `-DIERS_MODEL` selects GMF and the IERS Conventions 2010 solid-tide model; the latter requires linking the IERS FORTRAN routine `DEHANTTIDEINEL`.

## Demo5 positioning and ambiguity resolution

### Demo5 configuration-reference boundary

Appendix B's sample configuration still identifies itself as 2.4.2 and omits many Demo5 controls, so use the options in section 3.5/Appendix F or a configuration saved by a Demo5 application rather than treating that sample as exhaustive. Use Appendix F's configuration key spelling `pos2-minfixsats`.

### Static-start positioning and frequency mapping

`pos1-posmode=static-start` holds the rover static until the first fix, then switches to the kinematic model; receiver dynamics can still add velocity and acceleration states. Demo5 maps its dual- and triple-frequency choices by constellation as shown below, while the additional four-band choice including L6 is explicitly experimental and not fully supported.

```text
pos1-posmode   =static-start
pos1-frequency =l1+l2/e5b+l5/e5a
# GPS: L1/L2/L5; GLO: R1/R2; GAL: E1/E5b/E5a; BDS: B1/B2b/B2a
```

### Combined filtering with or without phase reset

The normal Combined post-processing mode resets phase-bias states before the backward pass to keep the two directions more independent; Demo5 also offers “Combined — no phase reset” to avoid reconvergence at the start of that pass. Combined output averages two fixes unless they disagree too much, uses the fixed direction when only one direction fixes, and averages with float status when both remain float.

### Multi-pass ambiguity resolution and satellite qualification

Demo5 ambiguity resolution can make up to three attempts per sample with different satellite sets; later attempts may omit GLONASS/SBAS or a newly acquired satellite, including a GPS-only retry after a GLONASS-inclusive failure. `pos2-arfilter=on` separately qualifies new or cycle-slip-returning satellites and delays one that materially degrades the AR ratio, rather than relying only on the blind sample delay in `pos2-arlockcnt`.

### Adaptive ratio and convergence gates

`pos2-arthres` is the nominal ratio threshold for eight satellite pairs; `pos2-arthresmin`/`pos2-arthresmax` bound a threshold that decreases with more pairs and increases with fewer, while setting all three equal makes it fixed. `pos2-arthres1` additionally prevents AR until the position-state variance reaches its configured limit; the options table's default is `0.25`.

```text
pos2-arthresmin =3
pos2-arthres    =3
pos2-arthresmax =3
pos2-arthres1   =0.25
```

### Fix, hold, and single-satellite exclusion floors

Demo5 defaults to at least four ambiguities for a fix, five for a hold, and ten before enabling its per-epoch trial exclusion of one satellite; when an exclusion significantly improves the ratio, that satellite is removed from AR. Appendix F spells the corresponding keys as follows:

```text
pos2-minfixsats  =4
pos2-minholdsats =5
pos2-mindropsats =10
```

### Hold feedback and sample-count units

`pos2-varholdamb` is the variance used by fix-and-hold pseudo-measurements and therefore acts as an inverse tracking gain: larger values weaken ambiguity feedback. `pos2-arlockcnt`, `pos2-arminfix`, and `pos2-aroutcnt` count samples rather than seconds, so their real-time duration changes with rover sample rate.

```text
pos2-varholdamb =0.1
```

### GLONASS inter-frequency-bias handling

Use `pos2-gloarmode=on` only when the receiver pair has compatible or zero GLONASS inter-frequency biases; `fix-and-hold` waits until the first GPS hold before nulling those biases, while `autocal` can use GLONASS immediately. Autocal takes the relative bias in metres per frequency slot from `pos2-arthres2`, its initial state variance from `pos2-arthres3`, and process noise from `pos2-arthres4`; `pos2-gainholdamb` controls bias-nulling gain in GLONASS Fix-and-Hold mode.

### Separate slip and innovation rejection controls

`pos2-dopthres` adds a Doppler-versus-carrier-phase cycle-slip threshold in hertz, with `0` disabling it. Demo5 also separates code and phase innovation rejection as `pos2-rejcode` and `pos2-rejionno`, whose documented defaults are 10 m and 2 m.

```text
pos2-dopthres =0
pos2-rejcode  =10
pos2-rejionno =2
```

### Matched real-time solution mode

Demo5 documents `pos2-syncsol=on` as a matched mode that waits until both rover and base/correction data are ready, accepting that output may lag rover time. The default `off` mode instead minimizes latency and extrapolates delayed base or correction data to the rover epoch.

### PPP option boundary

`pos1-posopt6` enables day-boundary clock-jump correction only for PPP modes. Treat `PPP-AR` as unsupported in Demo5 applications: the options table controls exposed availability, while the retained experimental CNES wide-lane FCB/IRC algorithm description does not establish a selectable mode.

### Extended observation-error model

Demo5 adds an L5 code/carrier error ratio as `stats-eratio5`, an SNR-dependent carrier-phase term `stats-errsnr * 10^(0.1 * (stats-snrmax - snr))`, and a u-blox-only receiver-uncertainty term `stats-errrcv`. The two added error terms default to zero, which disables their contribution until configured.

### Optional velocity solution fields

`out-outvel=on` appends north/east/up velocity and covariance-derived uncertainty fields to the normal text solution: `vn ve vu sdvn sdve sdvu sdvne sdveu sdvun`. Parsers must continue to follow the `%` field-indicator line because these columns are optional.

## Branch-aware post-processing

### Reproducing the upstream 2.4.3 branch

At the benchmarked 2.4.3 b33 point, the upstream source and executable repositories still defaulted to `master`, which yielded 2.4.2; a partial merge from 2.4.3 had not made the branches equivalent. Select the `2.4.3` branch explicitly when reproducing that release:

```sh
git clone --branch 2.4.3 https://github.com/tomojitakasu/RTKLIB.git
```

### Adaptive satellite admission is Demo5-only

Official 2.4.2 p13 and 2.4.3 b33 do not implement Demo5's `pos2-arfilter`, so the benchmark replaced adaptive admission with a fixed sample delay for its upstream runs. These values reproduce that experiment rather than define general defaults:

```text
# Demo5 b33b2
pos2-arfilter =on
pos2-arlockcnt=0
# official 2.4.2 p13 / 2.4.3 b33
pos2-arlockcnt=10
```

### Outlier thresholds are branch-specific

The upstream and Demo5 outlier detectors differ, so the same `pos2-rejionno` does not have equivalent behavior: the benchmark needed `30.0` upstream versus `1.0` in Demo5 b33b2. Retune this threshold for the branch and data rather than copying it unchanged.

### Galileo E5b occupies a different frequency slot in Demo5

Unlike Demo5's frequency mapping, official 2.4.2/2.4.3 keeps Galileo E5b in L7, which its solutions do not fully support. Frequency selections and observation handling can therefore change when the same data or configuration moves between upstream and Demo5.

## Measurement and correction configuration

### Signal-quality masks are endpoint- and frequency-specific

`pos1-snrmask-r` and `pos1-snrmask-b` independently enable rover and base SNR rejection. Each enabled frequency needs its own nine-value, five-degrees-per-bin threshold list, so a dual-frequency configuration must define both `pos1-snrmask_L1` and `pos1-snrmask_L2`.

```text
pos1-snrmask-r  =on
pos1-snrmask-b  =on
pos1-snrmask_L1 =35,35,35,35,35,35,35,35,35
pos1-snrmask_L2 =35,35,35,35,35,35,35,35,35
```

### Separate elevation gates for solution, fix, and hold

`pos1-elmask` gates the overall solution, `pos2-arelmask` can impose a stricter gate only on ambiguity resolution, and `pos2-elmaskhold` can exclude low satellites from hold feedback even when they participated in obtaining a fix. Setting the latter masks equal to `pos1-elmask` adds no further filtering.

### Antenna phase-center switches require matching metadata

`pos1-posopt1=on` applies satellite antenna PCV and requires the satellite PCV file; it is normally useful for PPP rather than short-baseline RTK. `pos1-posopt2=on` requires a receiver PCV file plus the configured rover and base antenna types, mainly affects height, and is unnecessary for a relative pair whose identical antenna effects cancel.

### Receiver uncertainty and code/phase weighting are distinct

`pos2-rcvstds=on` adds receiver-reported pseudorange and phase standard deviations to the elevation-based variance model and is supported only for u-blox input. `stats-eratio1` and `stats-eratio2` instead set the pseudorange-to-carrier-phase standard-deviation ratio; increasing them can converge faster but raises false-fix risk, so the `pos2-arthres1` convergence gate must be retuned with them.

### Dynamics noise should describe antenna motion

With rover dynamics enabled, `stats-prnaccelh` and `stats-prnaccelv` are one-sigma horizontal and vertical acceleration settings. Tune them from RTKPLOT acceleration data and include antenna vibration, bumps, and other high-frequency motion rather than only commanded rigid-body acceleration; underestimating them is worse than modest overestimation.

### Differential age and provisional base coordinates

`pos2-maxage` is the maximum rover/base measurement delay in seconds, so radio dropouts beyond it stop differential use even if ambiguity state remains healthy. When `ant2-postype=single`, `ant2-maxaveep` controls how many single-position samples form the base coordinate; using one freezes the provisional base instead of moving it while the filter converges, and can shorten time to first fix for RTCM input.

### Correction-model enum map

Embedded callers select atmospheric and satellite corrections with these exact constants and numeric values; `IFLC` is the L1/L2 or L1/L5 ionosphere-free combination, while `ESTG` estimates ZTD plus gradients.

```text
IONOOPT_OFF/BRDC/SBAS/IFLC/EST/TEC/QZS = 0/1/2/3/4/5/6
TROPOPT_OFF/SAAS/SBAS/EST/ESTG         = 0/1/2/3/4
EPHOPT_BRDC/PREC/SBAS/SSRAPC/SSRCOM   = 0/1/2/3/4
```

## Ambiguity-resolution safeguards

### Affected-build AR lock-count bug

In the affected RTKLIB code, a newly acquired satellite's lock counter is initialized to `-minlock`, but `ssat_t.lock` is unsigned; the value therefore wraps positive and the `lock > 0` test admits the satellite to ambiguity resolution immediately, making `pos2-arlockcnt` ineffective. The rtklibexplorer patch changes the counter to signed before relying on that delay:

```c
int lock[NFREQ]; /* lock counter of phase */
```

### Fix-and-hold makes AR diagnostics self-referential

Fix-and-hold pulls ambiguity states toward integers and then validates them by their closeness to integers, so percent-fixed and median AR ratio cease to be independent evidence of accuracy once holding begins. Feedback is applied every epoch and can make a wrong held solution difficult to release.

### Fix-and-Bump availability boundary

The source's “Fix-and-Bump” is an experimental one-epoch feedback modification, not a selectable Demo5 mode. Turning feedback off after that adjustment also does not immediately restore independent validation because the adjusted bias states persist; Demo5 instead exposes `pos2-varholdamb` to weaken continuous fix-and-hold feedback.
