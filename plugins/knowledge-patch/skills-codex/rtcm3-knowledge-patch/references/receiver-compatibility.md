# Receiver and processing-software compatibility

## Waypoint RTCM conversion

Waypoint's RTCM 3 converter accepts legacy GPS observations 1002/1004 and GLONASS observations 1010/1012, requiring one message from the applicable pair. It requires type 1013 to recover the GPS week number and recommends the applicable broadcast ephemeris messages.

Its multi-constellation path accepts MSM4 through MSM7 for GPS, GLONASS, Galileo, QZSS, and BeiDou. MSM4 and MSM6 omit Doppler; MSM6 and MSM7 use larger messages for higher precision.

## Qinertia ingest

Qinertia accepts RTCM 3 as kinematic-rover data or static-base/correction data. Its published MSM parser set includes MSM4, MSM5, and MSM7 for GPS, GLONASS, Galileo, QZSS, and BeiDou, but not MSM6. Its listed ephemeris inputs are GPS 1019, GLONASS 1020, and Galileo 1045/1046; QZSS 1044 and BeiDou 1042 are absent from that support list.

## Septentrio correction inputs

Septentrio receivers accept RTCM corrections through available hardware or network interfaces such as USB and Ethernet, or through the built-in NTRIP client when online. Published support includes legacy observation and station messages, type 1230, and every MSM1–MSM7 subtype for GPS, GLONASS, Galileo, SBAS, QZSS, and BeiDou.
