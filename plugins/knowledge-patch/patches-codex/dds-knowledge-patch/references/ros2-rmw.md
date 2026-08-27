# ROS 2 RMW Behavior

Source batch: `dds-ros2-rmw`.

## Discovery-derived QoS

`SYSTEM_DEFAULT` delegates a QoS policy to the active RMW or DDS
implementation. It does not establish one cross-implementation value.

`BEST_AVAILABLE`, in APIs that support it, derives policy values from
discovered endpoints. The result therefore depends on what has been discovered
when selection occurs and on the RMW's supported behavior.

Use explicit QoS profiles when behavior must remain predictable across RMW
implementations. In diagnostics, distinguish:

- an explicit policy chosen by the application;
- a `SYSTEM_DEFAULT` value resolved by the implementation;
- a `BEST_AVAILABLE` value derived from discovered endpoints.

Do not report any of these as interchangeable merely because communication
currently succeeds.

## Optional data-path capabilities

The following are optional RMW capabilities rather than universal guarantees:

- loaned messages;
- zero-copy or shared-memory paths;
- content filtering;
- unique network flow requirements.

Before using an optional path:

1. query whether the active RMW supports it;
2. handle an unsupported result explicitly;
3. retain a correct fallback where the application requires portability;
4. verify the actual transport and copy behavior rather than inferring it from
   the API name.

Switching RMW implementations does not guarantee preservation of a
product-specific zero-copy or shared-memory path. Recheck capability support,
eligibility constraints, QoS, and the available transport after any switch.
