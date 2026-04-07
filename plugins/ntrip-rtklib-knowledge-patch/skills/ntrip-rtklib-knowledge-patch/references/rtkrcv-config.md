# rtkrcv Configuration Reference

## Stream Configuration

### Input Streams

```conf
# 1=rover, 2=base, 3=corrections
inpstr1-type       = serial        # serial|tcpcli|tcpsvr|ntripcli|file|off
inpstr1-path       = /dev/ttyACM0:115200:8:n:1:off
inpstr1-format     = ubx           # ubx|rtcm3|rtcm2|nov|oem3|...
inpstr2-type       = ntripcli
inpstr2-path       = user:passwd@caster.example.com:2101/MOUNTPT
inpstr2-format     = rtcm3
```

### Output Streams

```conf
outstr1-type       = file
outstr1-path       = /tmp/solution_%Y%m%d%h%M.pos
outstr1-format     = llh           # llh|xyz|enu|nmea|...
```

### Log Streams (Raw Data)

```conf
logstr1-type       = file
logstr1-path       = /tmp/rover_%Y%m%d%h%M.ubx
```

### Server Parameters

```conf
svrcycle           = 10            # processing cycle (ms)
timeout            = 10000         # stream timeout (ms)
reconnect          = 10000         # reconnect interval (ms)
nmeacycle          = 5000          # NMEA GGA send cycle (ms) for VRS
buffsize           = 32768         # input buffer size (bytes)
```

## rtkrcv.conf Path Formats

Unlike str2str (which uses URI schemes), rtkrcv.conf sets the stream type separately and paths have no scheme prefix:

```
ntripcli : user:passwd@addr:port/mntpnt
ntripsvr : [passwd@]addr:port/mntpnt[:str]
ntripcas : user:passwd@:[port]/mpoint[:srctbl]
tcpsvr   : :port
tcpcli   : addr:port
serial   : port[:bit_rate[:byte[:parity(n|o|e)[:stopb[:fctr]]]]]
file     : path[::T[::+offset][::xspeed]]
```

## Demo5-Specific Configuration

The demo5 fork (rtklibexplorer/RTKLIB) adds parameters not in official 2.4.3. Build from `rtklibexplorer/RTKLIB`, not `tomojitakasu/RTKLIB`.

### Pseudorange/Carrier Ratio

```conf
# 300 for u-blox receivers (default 100)
stats-eratio1      = 300
stats-eratio2      = 300
```

### Fix-and-Hold Tuning

```conf
# Hold tracking gain (variance, higher = lower gain)
pos2-varholdamb    = 0.1           # default 0.001; 0.1-1.0 avoids false holds

# AR filter — delay new/cycle-slip sats if they degrade AR ratio
pos2-arfilter      = on

# Position variance threshold before enabling AR (avoids premature fix)
pos2-arthres1      = 0.004         # 0.004-0.10 typical

# Consecutive fix samples before hold (adjust with sample rate)
pos2-arminfix      = 20            # 5-20× sample rate
```

### GLONASS AR (Inter-Channel Bias)

```conf
pos2-gloarmode     = fix-and-hold  # or autocal with arthres2/3/4 set
pos2-arthres2      = 0.0           # GLONASS hw bias (m/freq slot)
pos2-arthres3      = 1e-9          # initial bias variance
pos2-arthres4      = 0.00001       # bias process noise
```

### Satellite Constraints

```conf
pos2-minfixsats    = 4
pos2-minholdsats   = 5
pos2-mindropsats   = 10
```
