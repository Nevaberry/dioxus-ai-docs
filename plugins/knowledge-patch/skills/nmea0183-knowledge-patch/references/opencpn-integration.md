# OpenCPN Integration

Use this reference when routing NMEA 0183 data into OpenCPN core, AIS target handling, or the Dashboard plugin. Core and Dashboard have different acceptance rules.

## Heading and variation selection

For `HDG`, OpenCPN uses the sentence's magnetic variation when both the numeric value and east/west flag are present. Otherwise it falls back, in order, to:

1. `RMC` variation;
2. manually configured variation; or
3. the WMM plugin.

For `THS`, OpenCPN uses only autonomous mode `A`. It ignores modes `E`, `M`, `S`, and `V`.

## Core input and route handling

The core input path recognizes:

```text
HDM HDG HDT THS RMB RMC WPL GGA GLL GSV VTG APB XTE
AIVDM AIVDO TTM TLL OSD FPROS
```

Incoming `RTE` is not processed.

Incoming `WPL` is converted to an AIS-APRS position report only when **Treat WPL sentences as APRS position reports** is enabled in AIS settings.

## Radar, buddy, and distress targets

Radar `TTM` and `TLL` reports are routed through the AIS decoder and presented like AIS targets. For `TLL`, OpenCPN ignores the target-number and reference-target fields.

`FPROS` supplies a GPSGate Buddy position:

```text
$FPROS,lat,N|S,lon,E|W,msl_alt_m,sog_kn,heading_deg,date,utc,buddy_name*hh
```

`CDDSC` and `CDDSE` distress-call sentences are only partially supported.

## Dashboard sentence coverage

The Dashboard plugin recognizes its own input set, including legacy meteorological forms:

```text
RMA RMB RMC GSV GGA GLL GNS ALM HDG HDM HDT DBT DPT MTW MDA MTA
VHW VLW VTG VDR RSA MWD MWV VWR VWT XDR ZDA TLL XTE BWW BWR BWC
BOD APA APB OSD
```

Do not infer Dashboard support from core support or vice versa.

## Dashboard MDA acceptance

From `MDA`, Dashboard reads only the second pressure value, expressed in bars, and only when it is within `0.8`–`1.1`. It ignores every other field.

## Dashboard XDR acceptance

Dashboard accepts only these exact type/range/unit/name combinations:

```text
P,0.8..1.1|800..1100,B,Barometer
C,value,C,TempAir|ENV_OUTAIR_T
A,-180..180,D,PTCH|PITCH
A,-180..180,D,ROLL
C,value,C,ENV_WATER_T
```

For these attitude groups, pitch is negative nose-down and roll is negative left. Preserve exact unit and transducer-name spelling when generating compatible `XDR`.
