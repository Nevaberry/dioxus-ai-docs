# Receivers and Antennas

## Receiver changes and access

RTKBase 2.7.0 supports Septentrio Mosaic-X5 firmware 4.15. The receiver's default
login is `basegnss` and its default password is `basegnss!`.

The Settings GUI has a TCP host address field that controls receiver exposure.
Choose the bind address deliberately: it determines whether the GNSS receiver is
accessible externally or blocked from external access.

When configuring a U-Blox ZED-F9P, RTKBase now sets its dynamic model to static.

## Patch-antenna placement and ground plane

Mount a patch antenna level with the geographic horizon and give it an
unobstructed sky view. If it lacks a large integrated ground plane, center it on
a conductive surface at least 10 cm across and ideally 15 cm across. A vehicle
roof is suitable. The ground plane improves skyward gain and reduces multipath.

## Receiver environment and baseline length

Keep the receiver board enclosed and out of direct sunlight or fan airflow;
temperature disturbances can reduce thermal stability.

For reliable centimeter-level operation, design for a rover-to-base distance of
about 10 km or less when possible and keep it below roughly 25 km.

## ZED-F9P raw observations

For manual raw-data capture, enable `UBX-RXM-RAWX` on the active interface and
verify it in u-center's packet viewer. Binary UBX messages do not appear in the
text viewer.

Record observations at 1 Hz. Many PPP services ignore or decimate faster data,
while a 24-hour 1 Hz `.ubx` capture is already about 300 MB.

For RTKLIB logging and later RINEX conversion, also enable `UBX-RXM-SFRBX`
navigation data, verify enabled constellations and measurement rate, and save the
configuration to flash with `CFG`. NMEA is not required for RINEX conversion, but
a VRS correction service needs GGA positions from the rover.

Disable unused UARTs where practical. A low baud configured on an unused UART can
constrain output bandwidth even when the active receiver connection is USB.

## U-Blox diagnostic recording

For reception or correction failures, record logs from both base and rover with
NMEA and these UBX messages enabled:

- `UBX-RXM-RTCM` for received corrections;
- `UBX-MON-COMMS` for interface state;
- `UBX-NAV-CLOCK` for receiver clock state; and
- `UBX-NAV-PVT` for position and navigation state.

This combination helps distinguish an antenna problem from a correction
transport problem or receiver misconfiguration.

## Unicore RTCM fallback

When a UM980-class receiver cannot provide a native stream that RTKLIB decodes,
use RTCM3 as RTKBase's primary input. Configure the receiver's USB-connected port
to emit MSM and constellation navigation messages plus `GPRMC`, then select
`rtcm3` as the input format.

Retain TCP port 5015 when gpsd/chrony depends on the default primary stream.

Native Unicore raw observations can instead be logged from a second receiver
port and converted to RINEX with Unicore Converter. The converter runs on Windows
and also works through Wine.

## RTK2GO source credentials

Do not start an RTK2GO source connection with the temporary registration
password. Wait until the mount point and permanent password are confirmed.
Repeated source connections with an expired temporary credential can cause the
source IP to be temporarily banned.
