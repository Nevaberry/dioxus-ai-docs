# SDK Migration and Platform Integration

## BLE platform contract

`BlePlatformDelegate` removes obsolete functions and changes its APIs to return
`CHIP_ERROR`. Platform implementations must update method sets, propagate
failures, and add explicit error handling. Platforms can also disable
BLE-related device events and query `BleLayer` state (since sdk-1.4.2.0).

## Data-model namespace and provider migration

APIs under `chip::app::InteractionModel` move to
`chip::app::DataModel`. At the same time, the abstraction formerly named
`DataModel` becomes `Provider`; do not confuse that class rename with the
namespace migration. `DataModel::Provider` gains invoke support and endpoint
device-type reporting (since sdk-1.4.2.0).

Event-list-attribute support is removed from the SDK and generated code.
Applications, templates, and generators must stop expecting that generated
facility (since sdk-1.4.2.0).

`RendezvousParameters` no longer carries PASE verifier bits. Remove code that
populates, reads, serializes, or tests those bits when upgrading to
sdk-1.5.0.0.

## Cluster implementation architecture

`ServerClusterShim` adapts legacy generated clusters to
`ServerClusterInterface`. Code-driven clusters also support optional-attribute
set abstractions plus dynamic and static endpoints. Use these pieces for an
incremental migration instead of rewriting every legacy cluster at once (since
sdk-1.5.0.0).

Soil Measurement is converted to a code-driven cluster and has changed
initial-value behavior. Update both generated-code assumptions and application
initialization logic (since sdk-1.5.0.0).

Thermostat events are represented in cluster XML, while Thermostat Suggestions
are added to the data model and SDK implementation. Regenerate consumers that
depend on the XML (since sdk-1.5.0.0).

## Platform and class-name changes

TCP is enabled for ESP as a v1.5 backport, so ESP builds using
sdk-1.5.1.0 can exercise the SDK TCP transport path.

`TlsCertificateManagementCluster` is renamed to
`TLSCertificateManagementCluster`. Update includes, declarations, type names,
and tests that retain the old capitalization (since sdk-1.5.1.0).

ESP32 ICD configuration options are corrected. Recheck existing build
configuration rather than assuming old option combinations remain valid (since
sdk-1.5.1.0).

## Python, Android, and Darwin integration

Commissionable-node discovery in Python uses `asyncio`. Controllers must await
the asynchronous discovery flow and update call sites that assumed synchronous
results (since sdk-1.4.2.0).

Android clients can access active-mode duration, active-mode threshold, and
idle-mode duration as part of the ICD timing APIs (since sdk-1.4.2.0).

Darwin exposes additional commissioning reads through
`MTRCommissioningParameters.readEndpointInformation` and supports multipack BLE
connections with multiple discriminators (since sdk-1.4.2.0).

## Thread Border Router integration

The SDK includes server support for the Thread Border Router Management cluster
and a generic Thread Border Router delegate. Platform implementations should
connect the delegate to their native border-router control plane rather than
reimplementing the cluster contract (since sdk-1.4.2.0).

## Migration verification

When upgrading:

1. Regenerate cluster code and inspect XML/schema versions.
2. Compile platform delegates to expose removed or changed virtual methods.
3. Search for `InteractionModel`, the former `DataModel` type,
   event-list-generated APIs, and the old TLS class capitalization.
4. Exercise Python, Android, Darwin, ESP, and ESP32 paths that the product
   actually ships.
5. Keep SDK implementation behavior distinct from specification conformance.
