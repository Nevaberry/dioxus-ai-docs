# ROS 2 RMW QoS and data paths

Use this reference when a ROS 2 design depends on discovered QoS or an
accelerated/filtered RMW path. The capabilities described here come from
`dds-ros2-rmw` and must be checked against the selected RMW implementation.

## Choose QoS resolution explicitly

`SYSTEM_DEFAULT` delegates a QoS policy to the RMW layer or its DDS vendor.
The resulting value can therefore vary when the RMW implementation or vendor
changes.

`BEST_AVAILABLE`, in APIs that support it, derives policy values from endpoints
found through discovery. It is discovery-dependent rather than a fixed,
implementation-independent profile.

Use explicit QoS profiles whenever behavior must be deterministic across RMW
implementations. Treat a switch of RMW provider as a compatibility change when
delegated or discovered policy selection is in use.

## Probe optional data-path capabilities

The following RMW capabilities are optional:

- loaned messages;
- zero-copy or shared-memory delivery;
- content filtering; and
- unique network-flow requirements.

Query the relevant capability before relying on it and handle an unsupported
result. Do not assume that selecting a different RMW implementation preserves
an acceleration or filtering path supplied by the previous vendor.

Keep the functional DDS network path valid even when a local optimization is
enabled. Test both the optimized and fallback paths when deployment topology
can make a loaned, shared-memory, zero-copy, filtered, or unique-flow request
ineligible.
