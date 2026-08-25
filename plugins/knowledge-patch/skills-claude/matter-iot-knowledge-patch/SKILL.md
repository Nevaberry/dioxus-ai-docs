---
name: matter-iot-knowledge-patch
description: Matter (IoT)
version: Matter 1.6
license: MIT
metadata:
  author: Nevaberry
---


# Matter IoT Compatibility Guide

Use this skill when implementing, upgrading, reviewing, or certifying Matter
devices, commissioners, controllers, bridges, or SDK integrations. Start with
the quick checks below, then load the reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [commissioning-fabrics-security.md](references/commissioning-fabrics-security.md) | Setup flows, QR and NFC onboarding, Wi-Fi USD, fabrics, credentials, access control, attestation, and certification boundaries |
| [networking-transport-icd.md](references/networking-transport-icd.md) | BLE integration, MRP, TCP, discovery, ICD behavior, diagnostics transfer, and network infrastructure |
| [data-model-platform-migrations.md](references/data-model-platform-migrations.md) | Data-model API changes, generated code, scenes, endpoint identity, reporting, cluster migrations, and test-harness corrections |
| [devices-energy-closures.md](references/devices-energy-closures.md) | Vacuums, closures, energy, metering, thermostats, soil measurement, and security sensors |
| [cameras-media.md](references/cameras-media.md) | Camera certification, streams, WebRTC, Push AV, recording, snapshots, PTZ, chimes, and ICE configuration |

## First decide which authority applies

- Treat a Matter specification release as the source of normative behavior and
  certification requirements.
- Treat an SDK tag as implementation guidance, migration behavior, generated
  code, platform support, and test-harness behavior.
- Do not infer conformance solely from an SDK feature. Confirm requirements in
  the authorized specification and test plan.
- When public announcements omit cluster IDs, encodings, conformance language,
  state machines, or test vectors, do not invent those details.
- Preserve fallbacks when a feature requires both device and commissioner
  support.

## Breaking upgrade checks

### SDK integrations

- Update `BlePlatformDelegate` implementations for removed obsolete methods,
  `CHIP_ERROR` returns, optional BLE-device-event suppression, and `BleLayer`
  state inspection.
- Move APIs formerly under `chip::app::InteractionModel` to
  `chip::app::DataModel`; account for the old `DataModel` abstraction becoming
  `Provider`.
- Remove dependencies on generated event-list-attribute support.
- Convert Python commissionable-node discovery integrations to `asyncio`.
- Stop storing or reading PASE verifier bits in `RendezvousParameters`.
- Rename source references from `TlsCertificateManagementCluster` to
  `TLSCertificateManagementCluster`.
- Regenerate Access Control metadata from XML cluster version 2, not version 3.
- Recheck ESP32 ICD build configuration and camera-generated code when moving
  to the later SDK tag.

### Security and privacy

- Perform Access Control authorization before checking whether a target exists;
  reversing the order leaks protected-target existence.
- During commissioning, allow ecosystems to consult Device Attestation
  Certificate revocation lists.
- Do not impose an unconditional ICAC requirement on commissioners where the
  operational-credential flow permits a chain without one.
- Update certification-derived discovery checks for TXT-record `T` keys and
  discriminator subtypes.

### Camera integrations

- Treat allocated AV streams as persistent resources.
- Enforce advertised audio/video usage constraints on allocation and
  modification.
- Start video with allocated parameters and validate stream modification and
  deallocation in the cluster implementation.
- Reject watermark or on-screen-display requests unless the corresponding
  capability is advertised.
- Revalidate recording configurations and update Push AV clip-upload ordering
  after upgrading.

## Commissioning quick reference

### Enhanced setup and multipacks

Enhanced Setup Flow lets a commissioner present localized manufacturer terms,
collect consent, return the response to the device, and let the device adjust
functionality. A commissioner that does not support this flow must retain the
manufacturer-application Custom Commissioning Flow fallback.

A single QR payload can describe several devices in a multipack. SDK
commissioners may also receive concatenated QR codes over BLE, and Darwin can
connect using multiple discriminators.

### NFC modes are not interchangeable

| Mode | What NFC carries | Other transport required? |
| --- | --- | --- |
| Onboarding tag | The same onboarding payload represented by QR or numeric setup codes | Yes, commissioning finishes elsewhere |
| SDK commissioning support | `SetupPayload` support, power-state indication, and platform commissioning management | Depends on the implemented SDK path |
| Bidirectional commissioning | The full commissioning exchange, including before full device power | No |

Do not turn a reverted SDK cherry-pick into released behavior. Check the exact
tag before claiming NFC support.

### Wi-Fi-only commissioning

Wi-Fi-only products may commission through Wi-Fi Unsynchronized Service
Discovery when the commissioner supports that path. Do not assume universal
commissioner support or silently remove another viable rendezvous path.

## Fabric and credential quick reference

- A controller may restore itself from an already stored fabric without
  resupplying its NOC chain.
- Joint Commissioning groundwork includes a Joint Commissioning Window, ICAC
  CSR issuance, cross-signing scaffolding, Joint Fabric status, and device
  Joint Fabric mode.
- Joint Fabric administration lets cooperating controllers share one fabric
  identity and one device fabric-table slot through coordinated common state.
- Do not invent the common datastore protocol or its failure semantics where
  public material does not define them.
- PSA integrations may use backed SPAKE2+ and persistent ICD server keys.
- Operational Credentials support includes Vendor ID verification payloads and
  signer certificates.

## Network and transport quick reference

- Account for the longer default Thread MRP retry interval and MRP use during
  Wi-Fi PAF commissioning; use analytics hooks when diagnosing retries.
- Control TCP server listening separately from other TCP behavior.
- Keep accepted server connections alive, close a connection on oversized
  input, and avoid advertising IPv4 when IPv4 and IPv6 ports differ.
- Use TCP for large messages, camera image data, and faster firmware transfer
  where the platform supports it.
- Treat ESP TCP enablement as an SDK backport rather than proof of universal
  platform support.
- For continuous operational discovery, do not stop MinMDNS browsing after the
  first result.

## ICD quick reference

- Handle check-in at boot, persistent-subscription checks, check-in backoff, and
  the updated `ICDManager` interface.
- Expose active-mode duration, active-mode threshold, and idle-mode duration to
  applications where supported.
- Use the maximum applicable `IdleModeDuration` returned by the SDK getter.
- For a LIT ICD server, subscription loss triggers a check-in attempt in
  addition to the normal lifecycle.

## Data-model quick reference

- `DataModel::Provider` supports invokes and endpoint device-type reporting.
- Bridged-device `KeepActive` information includes `StayActiveDuration`.
- Node capability changes caused by firmware or user action can notify
  controllers to re-evaluate configuration without recommissioning.
- Persistent endpoint unique IDs survive recommissioning and do not depend on
  the administrator.
- Quieter Reporting suppresses unnecessary intermediate or unchanged values
  across additional attributes and device types.
- Use `ServerClusterShim` and optional-attribute abstractions for incremental
  migration from legacy generated clusters to `ServerClusterInterface`.

## Device-feature quick reference

### Robot vacuums

Use the dedicated operational states and errors. Recheck sequential-command and
job-transition behavior against the authorized state machine.

### Closures

Model reusable sliding, rotating, and opening motions with single-panel,
dual-panel, or nested mechanisms. SDK closure commands include stop, step,
set-target, move-to, and dimension control; round targets to declared
resolution and enforce secure-state and latching constraints.

### Energy and metering

Distinguish electrical-energy tariff distribution from commodity-metering
server implementations. Support state-of-charge reporting and bidirectional
charging only when the relevant device behavior is implemented and certifiable.

### Thermostats

Thermostat Suggestions may be evaluated against preferences, demand-response
commitments, manual changes, and other context. Presets may be time-bounded, and
declined suggestions can return standardized explanations.

## Camera quick reference

- Camera capability includes two-way WebRTC media, local and remote access,
  STUN/TURN traversal, multiple streams, PTZ, privacy and detection zones, and
  local or cloud recording.
- One structured session can carry multiple independently optimized audio and
  video streams for recording, display, analysis, or separate lenses.
- Snapshot delivery can use HEIC; recorded-video uploads can use HLS or DASH
  through CMAF Interface-2.
- Represent installations whose PTZ home lies at an edge of the rotation range.
- Let controllers select a chime rather than always triggering the default;
  account for clarified intercom signaling and integrated chimes.
- Install parsed ICE server configuration through `PeerConnection` where the
  SDK provides that path.

## Upgrade workflow

1. Identify the normative Matter release and the exact SDK tag independently.
2. Locate each changed API, generated cluster, platform delegate, and test
   script used by the project.
3. Regenerate code where XML, ranges, command behavior, or cluster versions
   changed.
4. Preserve capability negotiation and fallback paths for commissioners,
   transports, media features, and optional overlays.
5. Add negative tests for access-control ordering, invalid recording
   combinations, unsupported overlays, oversized TCP messages, and closure
   safety constraints.
6. Re-run certification tests against the matching authorized test plan.
7. Use the topic references for the detailed behavior behind each check.
