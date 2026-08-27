---
name: matter-iot-knowledge-patch
description: Matter (IoT)
version: "Matter 1.6"
license: MIT
metadata:
  author: Nevaberry
---


# Matter IoT Development Guide

Use this skill when implementing or upgrading a Matter controller, commissioner,
accessory, bridge, camera, network-infrastructure device, or certification
harness. It emphasizes compatibility-sensitive behavior, SDK migrations, and
the difference between specification capabilities and SDK implementation tags.

## How to use this skill

1. Identify whether the work targets the Matter specification, the
   connectedhomeip SDK, or both.
2. Confirm the exact specification and SDK tag used by the project.
3. Read the topic reference that matches the subsystem being changed.
4. Apply breaking migrations before enabling new features.
5. Validate normative behavior against the authorized specification and test
   plan for the product's certification target.
6. Regenerate data-model code after XML or schema changes instead of preserving
   stale generated artifacts.

Public announcements and SDK release tags are useful implementation guides, but
they do not replace normative conformance text, cluster definitions, test
vectors, or certification requirements.

## Reference index

| Reference | Topics |
| --- | --- |
| [Commissioning and security](references/commissioning-and-security.md) | Setup flows, QR and NFC, BLE and Wi-Fi rendezvous, fabrics, credentials, access control, revocation, certification |
| [SDK migration and platform integration](references/sdk-migration-and-platforms.md) | Renamed and removed APIs, generated code, delegates, platform configuration, controller and test-harness changes |
| [Transport, discovery, and reliability](references/transport-discovery-and-reliability.md) | ICD lifecycle, MRP, TCP, BDX, discovery, reporting, endpoint identity, network handoff |
| [Camera and media](references/camera-and-media.md) | Camera device types, WebRTC, streams, Push AV, recording, snapshots, chimes |
| [Devices, energy, and climate](references/devices-energy-and-climate.md) | Robot vacuums, closures, EVSE, tariffs, metering, soil, thermostats, scenes, security sensors |

## Breaking changes and deprecations

Address these early in an SDK upgrade:

- Update `BlePlatformDelegate` implementations for removed functions,
  `CHIP_ERROR` returns, and explicit error handling.
- Move APIs from `chip::app::InteractionModel` to
  `chip::app::DataModel`.
- Treat the former `DataModel` abstraction as `Provider`; implement invoke and
  endpoint device-type reporting where required.
- Remove dependencies on generated event-list-attribute support.
- Convert Python commissionable discovery integrations to `asyncio`.
- Remove all reads and writes of PASE verifier bits from
  `RendezvousParameters`.
- Update the TLS cluster class name to
  `TLSCertificateManagementCluster`.
- Generate Access Control metadata with cluster XML version 2.
- Recheck ESP32 ICD configuration and the platform's TCP enablement.
- Regenerate camera code and configuration after range, validation, or
  recorded-clip sequencing changes.

Do not infer released NFC behavior from a cherry-picked change that was reverted
before an SDK tag. Check the final tag and the product's intended NFC mode.

## Commissioning path selection

| Need | Applicable path | Critical constraint |
| --- | --- | --- |
| Standard printed onboarding | QR or numeric setup code | Keep a recoverable code available after installation |
| One scan for a product multipack | Concatenated multi-device QR data | Commissioner and BLE platform must support multipack parsing and discriminators |
| Tap to obtain onboarding data | NFC onboarding payload | The early tag-only form still needs another commissioning transport |
| Commission without BLE | Wi-Fi USD | Both product and commissioner must support USD commissioning |
| Complete commissioning over NFC | Bidirectional NFC | Supports the exchange even before a device is fully powered |
| Manufacturer terms and consent | Enhanced Setup Flow | Preserve Custom Commissioning Flow fallback for commissioners without support |
| Shared multi-controller administration | Joint Fabric | Controllers share one fabric identity and must coordinate common state |

When presenting user-directed commissioning data, honor the passcode display
length supplied with the message. When commissioning asks Network
Commissioning to join a new network, account for the SDK disconnecting the
previous network first.

## Security and privacy checks

- Consult device-attestation certificate revocation data during commissioning.
- Support partitioned CRLs when scaling independently updated revocation data.
- Perform Access Control authorization before revealing whether a protected
  target exists.
- Use Vendor ID verification payload generation, PEM encoding, signer
  certificates, and Operational Credentials support as one coherent flow.
- Apply corrected `AddNOC` ICAC behavior; do not require every commissioner
  chain to contain an ICAC where the test case permits omission.
- Treat Access Restriction Lists as controls for sensitive
  network-infrastructure settings and data.
- Preserve PSA-backed SPAKE2+ and persistent ICD key storage when the platform
  uses PSA credentials.

Network-infrastructure products have concrete capacity and feature minima.
Verify Thread and Wi-Fi requirements from the certification material, including
the corrected Proxy ARP/NDP requirement rather than assuming Target Wake Time.

## Transport and reliability checklist

- Gate TCP server listening independently from other TCP behavior.
- Enable keepalive on accepted server connections.
- Close a connection after an oversized inbound message.
- Do not advertise IPv4 when the IPv4 and IPv6 listening ports differ.
- Size configurable Diagnostic Logs BDX blocks for both controller and device.
- Use full TCP transport for large media, firmware, and data transfers where
  supported.
- Account for the increased default Thread MRP retry interval and MRP use in
  Wi-Fi PAF commissioning.
- Wire MRP analytics hooks into observability when diagnosing retransmissions.
- Keep operational discovery running when continuous results are required.
- Use asynchronous Python discovery rather than a blocking compatibility shim.

For intermittently connected devices, handle boot check-in, persistent
subscriptions, check-in backoff, active and idle timing, and subscription-loss
recovery together. The idle-mode getter returns the maximum applicable
duration, not necessarily a single raw configured value.

## Reporting and controller identity

Quieter Reporting may suppress unchanged or intermediate values for more
attributes and device types. Do not interpret the absence of every intermediate
report as a failed subscription.

Controllers should respond to node reconfiguration notifications by
re-evaluating capability state without automatically recommissioning. Use
persistent endpoint unique IDs to reconcile endpoints across recommissioning
and avoid duplicate controller or cloud representations.

Standardized capability and operational-limit reporting should drive feature
discovery and bounds checking. Avoid hard-coding support solely from the device
type.

## Camera upgrade checklist

- Model allocated camera AV streams as persistent resources.
- Enforce audio/video usage constraints during allocation and modification.
- Start video with the allocated parameters and update range parameters on
  reuse.
- Report snapshot and video modifications correctly to subscribers.
- Reject watermark or on-screen-display requests unless the capability is
  advertised.
- Install parsed ICE server configuration through `PeerConnection`.
- Support multi-stream structured sessions when consumers need different media
  qualities.
- Validate pan/tilt ranges, edge-home behavior, recording combinations, and
  recorded-clip upload order against current generated definitions.
- Use HEIC for snapshots and HLS or DASH through CMAF Interface-2 where the
  selected media-delivery mode requires them.
- Distinguish selectable chime sounds from an always-default chime and include
  integrated-chime/intercom signaling requirements.

## Device-domain highlights

Robot Vacuum Cleaner implementations must use the dedicated operational states
and errors and follow the revised sequential-command and job-transition state
machine.

Closure implementations compose sliding, rotating, and opening motions. Round
targets to declared resolution and reject motion that violates secure-state or
latching constraints.

Energy applications can combine EVSE Plug and Charge, RFID, state-of-charge,
bidirectional charging, commodity metering, electrical tariffs, grid data, and
power limits. Treat groundwork in an SDK as distinct from a certifiable
specification capability.

Thermostats can expose suggestions and events. Context-aware control evaluates
preferences, demand response, recent manual changes, and time-bounded presets,
and can return a standardized reason for declining a suggestion.

## Implementation discipline

- Use the project manifest and lockfile to establish the actual SDK tag.
- Inspect generated XML/schema outputs before changing application code.
- Separate provisional attributes from stable certifiable behavior.
- Treat SDK backports as tag-specific implementation behavior.
- Exercise both supported and unsupported commissioner capability paths.
- Test privacy-preserving error ordering with unauthorized callers.
- Test transport failure paths, not only successful commissioning.
- Re-run the appropriate certification scripts after discovery, credential,
  or data-model changes.
