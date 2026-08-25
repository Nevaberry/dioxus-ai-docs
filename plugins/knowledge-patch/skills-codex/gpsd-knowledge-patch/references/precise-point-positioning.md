# Precise Point Positioning

### Version and raw-observation prerequisites
The documented workflow requires GPSD 3.26 or later and computes a static position after collection rather than real-time RTK. `gpsrinex` PPP needs raw observations that GPSD can decode: UBX-RXM-RAWX or Javad GREIS can supply L1-only processing, while dual-frequency processing requires L1 and L2 observations from GREIS or a u-blox 9-series receiver.

### Long-run averaging with gpsprof
Any receiver with a stable 3D fix can instead be averaged by collecting 2,880 samples over 24 hours and rendering `gpsprof`'s plot, which includes mean position and error statistics; the post-processing host needs Python and gnuplot. A remote run uses the optional host argument after starting the remote daemon with network access enabled by `-g`.

```sh
gpsprof -n 2880 -T pngcairo > scatter.plot
gnuplot < scatter.plot > scatter.png

gpsprof -n 2880 -T pngcairo gps-host > scatter.plot
```

### u-blox 7/8 RAWX collection setup
For u-blox 7/8, raise a serial link to at least 57,600 baud, restrict a u-blox 8 to GPS and QZSS or it will not emit raw measurements, then enable and verify RAWX. This is not GPSD's default receiver configuration, so restarting the daemon loses the collection setup and requires repeating it.

```sh
gpsctl -s 115200
ubxtool -d GLONASS -d BEIDOU -d GALILEO -d SBAS -e GPS
ubxtool -p CFG-GNSS
ubxtool -e RAWX
ubxtool | fgrep RAWX
```

### Javad GREIS collection setup
For a GREIS receiver, use `zerk` to raise the serial speed, disable the existing message set, enable raw reports, limit constellations to those accepted by the target PPP service, and verify both the constellation state and `[PC]` carrier-phase reports. Restarting GPSD likewise restores its normal configuration and requires this setup again.

```sh
zerk -S 115200
zerk -p DM
zerk -e RAW
zerk -d COMPASS
zerk -d GALILEO
zerk -d SBAS
zerk -e GPS
zerk -p CONS
zerk -v 2 | fgrep '[PC]'
```

### RINEX 3 acquisition cadence
After receiver setup, `gpsrinex` can record 24 hours as 2,880 observations at 30-second intervals; collecting faster than 30 seconds may degrade PPP results, and Trimble RTX reduces input faster than 10 seconds to 10-second intervals. Keep the receiver and daemon configuration intact for the whole capture.

```sh
gpsrinex -i 30 -n 2880 -f today.obs
```

### CSRS-PPP submission contract
CSRS-PPP accepts L1-only RINEX 3 input: submit the observation file in Static mode with ITRF selected, and retain the chosen horizontal datum, vertical datum, and coordinate epoch when using the result. Newly collected data may need 10–60 minutes before processing, while waiting about two weeks makes final orbit products available; as of July 2025 its accepted observation codes are:

```text
GPS: C1C L1C C2C L2C C1W L1W C2W L2W C1L L1L C2L L2L C2S L2S C1X L1X C2X L2X
GLONASS: C1C L1C C2C L2C C1P L1P C2P L2P
Galileo: C1X L1X C5X L5X C1C L1C C5Q L5Q
```

### Other PPP service constraints
Trimble RTX instead requires L1 and L2 pseudorange and carrier-phase observations, accepts 10 minutes through 24 hours while recommending at least 60 minutes, and requires renaming `today.obs` to the RINEX-style `today.YYo` suffix for two-digit year `YY`. GAPS requires L2 P or L5 I+Q observations and is not supported by GPSD's documented receiver path, while OPUS requires L1/L2 observations and has limited US-only coverage.

