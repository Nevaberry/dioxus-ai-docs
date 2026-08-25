# Desktop Operation and Networking

## Independent safety controls

AgOpenGPS is described as a demonstration and simulator system without
built-in safety limits. Installers and operators must supply an independent
way to stop automatic control and keep people clear of moving equipment.

GNSS reception, RTK fix, coverage painting, or a responsive steering loop
shows that one technical layer works. None establishes safe operation.

## Portable Windows releases

Desktop releases are portable archives rather than installers:

1. Unblock the downloaded ZIP when Windows requires it.
2. Extract the complete archive to a normal writable directory.
3. Run `AgOpenGPS.exe` from the extracted files, never from inside the archive.

AgIO can be launched independently to isolate communication failures from the
guidance application.

## Section capacities

The 6.8.5 desktop application supports either:

- up to 16 individually sized sections; or
- up to 64 equal sections.

Its guidance uses pure pursuit. Do not infer 64 physical controller outputs
from the application's 64-section representation.

## Layered AgIO diagnosis

Work outward from the source:

1. Check incoming NMEA and position/fix status.
2. Check the NTRIP connection and received correction bytes.
3. Check the selected serial or UDP correction outputs and module status.
4. Then investigate guidance or steering inside AgOpenGPS.

The AgIO serial monitor can display and log traffic. `115200` baud is common
for Teensy modules, while `38400` is common for older Arduino modules. The UDP
monitor can filter or log NTRIP, NMEA, and UDP traffic. Use those views to
separate data reaching AgIO from data reaching a hardware module.

## Dedicated Ethernet subnet

Ethernet modules conventionally use `192.168.5.0/24`:

- put the Windows Ethernet adapter and every module on that subnet;
- give every module a unique address;
- enable UDP in AgIO;
- do not assign two PC adapters to the same subnet.

When the module path fails, verify physical link, adapter state and subnet
mask, module addresses, monitored ports and messages, and board-specific
network firmware. Working Wi-Fi or Internet access says nothing about this
dedicated path.
