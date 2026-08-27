# Data Model and Platform Migrations

Use this reference when upgrading SDK interfaces, generated code, reporting,
endpoint identity, cluster versions, or compatibility test harnesses.

## Interaction-model API migration

APIs under `chip::app::InteractionModel` move to `chip::app::DataModel`. The
previous `DataModel` abstraction is renamed `Provider`.
`DataModel::Provider` gains invoke support and endpoint device-type reporting.
Update namespaces, implementations, and call sites together
(sdk-1.4.2.0).

## Generated event-list removal

Event-list-attribute support is removed from the SDK and generated code.
Applications and generators must stop depending on the facility when upgrading
(sdk-1.4.2.0).

## Legacy cluster migration

`ServerClusterShim` adapts legacy generated clusters to
`ServerClusterInterface`. Code-driven clusters gain optional-attribute set
abstractions and support both dynamic and static endpoints. These facilities
allow an incremental migration rather than an all-at-once rewrite
(sdk-1.5.0.0).

## Code-driven Soil Measurement

Soil Measurement moves to a code-driven cluster and changes its initial-value
behavior. Generated-code consumers must account for both the implementation
model and initial-value change (sdk-1.5.0.0).

## Access Control XML version

The Access Control cluster XML version is corrected from 3 to 2. Metadata and
generated code derived from the tag must use cluster version 2
(sdk-1.5.1.0).

## TLS cluster class capitalization

`TlsCertificateManagementCluster` is renamed to
`TLSCertificateManagementCluster`. Update includes, type references,
registrations, and any generated bindings that retain the old capitalization
(sdk-1.5.1.0).

## Reporting behavior

### Quieter Reporting

Quieter Reporting extends reporting optimizations to more attributes and
device types. It suppresses unnecessary intermediate or unchanged values to
reduce network traffic and battery use (1.4.2).

### Time-based scenes

Scenes have standardized, certifiable time-based behavior. Controllers can
define their own scenes and coordinate transitions with fewer commands
(1.4.2).

### Camera subscription corrections

Camera video and snapshot modifications produce corrected subscription
reports. Camera-specific lifecycle behavior is in
[cameras-media.md](cameras-media.md) (sdk-1.5.0.0).

## Node reconfiguration

A node can notify controllers when firmware or user changes alter its
capabilities. Controllers can then re-evaluate their configuration without
recommissioning the device (1.4.2).

## Persistent endpoint identity

Endpoint unique IDs are administrator-independent and survive recommissioning.
Controllers and cloud-linked ecosystems can recognize an existing endpoint
instead of creating a duplicate representation (1.4.2).

## Capability and operational-limit reporting

Devices can report supported capabilities and operational limits in a
standardized form. Controllers can discover both what a device supports and
the bounds within which it can operate (1.6).

## Commissioning test-harness migration

The later SDK scripts update TXT-record `T`-key verification and correct
discriminator-subtype lookup in TC-SC-4.1 and TC-SC-4.3. Custom harnesses need
equivalent behavior (sdk-1.5.1.0).

TC-SC-3.5 permits a commissioner DUT without an ICAC in its chain in allowed
cases. Do not encode an unconditional ICAC requirement in the harness
(sdk-1.5.1.0).
