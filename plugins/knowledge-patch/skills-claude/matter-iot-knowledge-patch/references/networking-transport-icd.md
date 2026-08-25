# Networking, Transport, and ICD Behavior

Use this reference for platform BLE contracts, discovery, reliable messaging,
TCP, diagnostic transfer, intermittent connectivity, and infrastructure device
requirements.

## BLE platform integration

`BlePlatformDelegate` removes obsolete functions, and its APIs return
`CHIP_ERROR`. Platform implementations must update their method sets, return
handling, and error propagation. Platforms may also disable BLE-related device
events and inspect `BleLayer` state (sdk-1.4.2.0).

BLE commissioning APIs for multipack payloads and commissioner attribute reads
are detailed in
[commissioning-fabrics-security.md](commissioning-fabrics-security.md).

## Reliable messaging

The default MRP retry interval for Thread is increased. Wi-Fi PAF commissioning
also enables MRP, and analytics hooks allow implementations to observe retry
and protocol behavior (sdk-1.4.2.0).

## TCP server and connection behavior

TCP server listening has a separate enable control. Accepted server
connections use TCP keepalive. Receiving an oversized message closes the
connection. A node does not advertise IPv4 addresses when the IPv4 and IPv6
ports differ (sdk-1.4.2.0).

Full TCP transport supports large messages and data sets, including camera
image data and faster firmware transfers (1.5).

TCP support is enabled for ESP as a v1.5 backport. Treat this as support in the
specific SDK/platform combination rather than assuming every platform build
enables TCP (sdk-1.5.1.0).

## Diagnostic Logs transfer

The maximum BDX block size for Diagnostic Logs is configurable on controllers
and devices. Deployments may tune both ends instead of relying on one fixed SDK
limit (sdk-1.5.0.0).

## Operational and commissionable discovery

Linux operational discovery can run continuous queries, and MinMDNS browsing
continues after the first result instead of ending the search immediately
(sdk-1.4.2.0).

Python commissionable-node discovery uses `asyncio`. Controller integrations
must await the asynchronous discovery flow rather than relying on the previous
synchronous interface (sdk-1.4.2.0).

Certification-script changes for TXT-record `T` keys and discriminator
subtypes are documented in
[commissioning-fabrics-security.md](commissioning-fabrics-security.md).

## Thread Border Router Management

The SDK supplies server support for the Thread Border Router Management cluster
and a generic Thread Border Router delegate. Platform implementations can use
the delegate as their integration boundary (sdk-1.4.2.0).

## Network infrastructure requirements

A Thread Border Router included in a Network Infrastructure Manager must
support at least 150 devices and be certified for Thread 1.4. A Wi-Fi access
point must support 100 simultaneous associations, Extended Sleep, and Proxy
ARP/NDP. The corrected requirement is not Target Wake Time (1.4.2).

Access Restriction Lists for infrastructure devices are covered in
[commissioning-fabrics-security.md](commissioning-fabrics-security.md).

## ICD lifecycle and timing

### Check-in lifecycle

The SDK adds ICD check-in at boot, persistent-subscription checks, check-in
backoff, and an updated `ICDManager` interface. Applications, including Android
clients, can access active-mode duration, active-mode threshold, and idle-mode
duration (sdk-1.4.2.0).

### Duration selection and subscription loss

The ICD getter returns the maximum applicable `IdleModeDuration`. A LIT ICD
server also attempts a check-in when its subscription disappears, providing a
recovery trigger outside the normal check-in lifecycle (sdk-1.5.0.0).

### ESP32 configuration

ESP32 ICD configuration options are corrected in the later SDK tag. Recheck
existing ESP32 ICD build configuration when upgrading (sdk-1.5.1.0).

## Bridged-device active periods

Bridged-device information adds `StayActiveDuration` to `KeepActive`, allowing
the requested active period to accompany a keep-active operation
(sdk-1.4.2.0).
