# Desktop Operation and Networking

## Safety boundary

AgOpenGPS is described as a demonstration/simulator system without built-in
safety limits. Installers and operators must supply an independent method to
stop automatic control and keep people clear. GNSS reception, RTK fix, coverage
painting, or a responsive steering loop does not establish safe operation.

## Portable Windows installation

Desktop releases are portable archives. Unblock the downloaded ZIP when needed,
extract the whole archive to a normal writable directory, and run
`AgOpenGPS.exe` from the extracted files. Do not run it from inside the archive.
AgIO can be launched independently to separate communications faults from
guidance application faults.

## Section capacity and guidance

The 6.8.5 desktop application supports either 16 individually sized sections or
64 equal sections. It uses pure-pursuit guidance. Application support for 64
sections does not by itself mean a connected controller has 64 physical outputs.

## Layered AgIO diagnosis

Follow the data path in order:

1. Check incoming NMEA, parsed position, and fix status.
2. Check the NTRIP connection and whether correction bytes arrive.
3. Check the selected serial or UDP correction outputs.
4. Check module status and traffic reaching the hardware.
5. Investigate guidance and steering in AgOpenGPS only after the prior layers.

AgIO's serial monitor can display and log traffic. `115200` baud is common for
Teensy modules; `38400` is common for older Arduino modules. Its UDP monitor can
filter or log NTRIP, NMEA, and UDP traffic, separating data that reaches AgIO
from data that reaches hardware.

## Dedicated Ethernet subnet

Ethernet modules conventionally use `192.168.5.0/24`. Put the Windows Ethernet
adapter and each uniquely addressed module on that subnet, enable UDP in AgIO,
and avoid assigning two PC adapters to the same subnet.

When traffic fails, verify physical link, adapter state and mask, unique module
addresses, monitored ports and messages, and the board-specific network
firmware. Working Wi-Fi or Internet connectivity says nothing about the
dedicated module path.

