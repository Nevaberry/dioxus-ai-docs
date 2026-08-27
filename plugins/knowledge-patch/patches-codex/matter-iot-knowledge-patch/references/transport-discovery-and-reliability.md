# Transport, Discovery, and Reliability

## Intermittently connected devices

`KeepActive` bridged-device information includes `StayActiveDuration`, allowing
the requested active period to accompany the operation (since sdk-1.4.2.0).

The ICD lifecycle includes check-in at boot, persistent-subscription checks,
check-in backoff, and an updated `ICDManager` interface. Applications can query
active-mode duration, active-mode threshold, and idle-mode duration (since
sdk-1.4.2.0).

The ICD getter returns the maximum applicable `IdleModeDuration`. A LIT ICD
server also attempts a check-in when its subscription disappears, creating a
recovery trigger in addition to its normal lifecycle (since sdk-1.5.0.0).

## MRP behavior and observability

The default MRP retry interval for Thread is increased. Wi-Fi PAF commissioning
also enables MRP. Validate timeout expectations and retry-sensitive tests after
an upgrade (since sdk-1.4.2.0).

MRP analytics hooks expose protocol behavior for instrumentation. Connect them
to diagnostics when investigating retransmission, latency, or reachability
problems (since sdk-1.4.2.0).

## TCP behavior

TCP server listening has an independent enable control. Accepted server
connections use TCP keepalive, oversized received messages close the
connection, and IPv4 is not advertised when the IPv4 and IPv6 ports differ
(since sdk-1.4.2.0).

Matter supports full TCP transport for large messages and data sets, including
camera images and faster firmware transfers (since 1.5).

ESP receives the TCP transport path as a v1.5 backport in sdk-1.5.1.0.
Enable and test it explicitly in platform configuration.

## BDX and diagnostic transfers

The maximum BDX block size for Diagnostic Logs is configurable on controllers
and devices. Tune both endpoints and test their negotiated behavior instead of
assuming one fixed SDK limit (since sdk-1.5.0.0).

## Operational and commissionable discovery

Linux operational discovery supports continuous queries. MinMDNS browsing
continues after its first result, so callers should decide when to stop rather
than assuming the browser completes after one node (since sdk-1.4.2.0).

Python commissionable discovery is asynchronous. Integrations must use the
`asyncio` flow and correctly manage cancellation, timeouts, and result
collection (since sdk-1.4.2.0).

Certification discovery scripts use updated TXT-record `T`-key verification and
correct discriminator-subtype lookup; see the commissioning reference for the
affected harness cases (since sdk-1.5.1.0).

## Network handoff

When Network Commissioning connects to a new network, the SDK first disconnects
the currently connected network. Applications must tolerate the intentional
connectivity gap and preserve enough state to complete or recover the operation
(since sdk-1.4.2.0).

## Reporting and reconfiguration

Quieter Reporting applies reporting optimizations to more attributes and device
types. It suppresses unnecessary unchanged or intermediate values, reducing
network traffic and battery use. Subscription consumers must not require every
intermediate value (since 1.4.2).

A node can notify controllers when firmware or user changes alter its
capabilities. A controller should re-read and reconcile relevant configuration
without automatically recommissioning the node (since 1.4.2).

Endpoint unique IDs are independent of the administrator and survive
recommissioning. Use them to recognize an endpoint and avoid duplicate
representations in a controller or linked cloud system (since 1.4.2).

Devices can report capabilities and operational limits in a standardized form.
Controllers should discover support and validate values against those reported
bounds rather than relying only on device-type assumptions (since 1.6).

