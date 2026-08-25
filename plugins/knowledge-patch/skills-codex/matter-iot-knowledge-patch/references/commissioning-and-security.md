# Commissioning and Security

## Setup flows and onboarding media

Enhanced Setup Flow lets a commissioner present localized manufacturer terms,
collect consent, and return the response to the device, which may alter its
functionality. A commissioner that does not support this flow must retain the
existing Custom Commissioning Flow through the manufacturer's application
(since 1.4.1).

A single setup QR code can encode onboarding information for multiple devices.
A compatible commissioner can therefore commission a multipack from one scan
rather than scanning each product separately (since 1.4.1).

Manufacturers can put the same onboarding payload used by Matter QR codes into
an NFC tag. This makes the setup payload recoverable when a printed code becomes
inaccessible after installation. The original NFC form carries onboarding data
only and still needs another transport to complete commissioning (since 1.4.1).

The SDK later added concatenated-QR BLE commissioning APIs and Darwin BLE
connections using multiple discriminators. A commissioner can request extra
attributes during commissioning; Darwin exposes this with
`MTRCommissioningParameters.readEndpointInformation` (since sdk-1.4.2.0).

Wi-Fi-only products may commission through Wi-Fi Unsynchronized Service
Discovery without a BLE radio, but only when the commissioner also supports
USD commissioning (since 1.4.2).

User-directed commissioning messages contain a passcode-display-length field.
The receiver should use it to size the commissioning UI rather than assuming a
fixed number of characters (since sdk-1.5.0.0).

The SDK's `SetupPayload`, `IsCommissioningWithoutPower`, and Android NFC
commissioning manager provided an SDK-level NFC path beyond merely formatting
an onboarding payload (since sdk-1.5.0.0).

The NFC delta briefly cherry-picked into the next SDK line was reverted before
the release tag. It has no net released behavior and must not be treated as
extra NFC support in sdk-1.5.1.0.

Bidirectional NFC can carry the complete commissioning exchange, including
before a device is fully powered. Unlike the onboarding-tag form, this mode
does not need another transport and can provision fixtures or in-wall products
before installation or power-up (since 1.6).

## Terms, access, and privacy

General Commissioning includes the provisional `TCUpdateDeadline` attribute.
Code that uses the attribute must retain provisional handling in
sdk-1.4.2.0.

Access Restriction Lists let Network Infrastructure Manager products restrict
sensitive settings and data to trusted, verified controllers (since 1.4.2).

The SDK checks Access Control before checking whether a write or command target
exists. Preserve this ordering so an unauthorized caller cannot infer the
existence of a protected target from the response (since sdk-1.5.0.0).

The Access Control cluster XML version is 2, correcting an erroneous value of
3. Regenerate metadata and code with version 2 when using sdk-1.5.1.0.

## Attestation, credentials, and revocation

The crypto layer supports PSA-backed SPAKE2+ and storage of persistent ICD
server keys in PSA storage (since sdk-1.4.2.0).

`CHIPCryptoPAL` can generate Vendor ID verification payloads and PEM-encode
them. The Operational Credentials cluster implements Vendor ID verification
and supports signer certificates (since sdk-1.4.2.0).

During commissioning, ecosystems can consult Certificate Revocation Lists to
detect revoked Device Attestation Certificates and warn about or block affected
devices (since 1.4.2).

Partitioned CRLs split revocation data into independently updated portions,
allowing the revocation mechanism to scale (since 1.6).

The crypto layer also supports single-part AEAD operations. A provider can
perform an authenticated encrypt or decrypt as one operation rather than being
forced through a multipart API (since sdk-1.5.0.0).

Correct operational-credential setup uses the fixed `AddNOC` ICAC behavior.
The TC-SC-3.5 commissioner test also accepts a commissioner DUT without an ICAC
in its chain where permitted; a harness must not impose an unconditional ICAC
requirement (since sdk-1.5.1.0).

## Fabrics and controller administration

The initial Linux `fabric-admin` tool provides administration for Fabric
Synchronization (since sdk-1.4.2.0).

A controller can be restored from an already stored fabric without supplying
the NOC chain again (since sdk-1.4.2.0).

Joint commissioning groundwork includes:

- opening a Joint Commissioning Window through `CommissioningWindowManager`;
- ICAC CSR generation and issuance;
- Joint Commissioning Method cross-signing scaffolding;
- Joint Fabric status and data-model support; and
- Joint Fabric mode through `DeviceInstanceInfoProvider`.

These implementation pieces arrive in sdk-1.5.0.0.

Joint Fabric allows multiple controllers to share one fabric identity and a
common datastore, consuming one device fabric-table slot instead of one per
ecosystem. The controllers must coordinate their state and administration. The
public description does not define the datastore protocol or its failure
semantics, so implementation needs the normative material (since 1.6).

## Discovery and certification harnesses

The TC-SC-4.1 and TC-SC-4.3 scripts use updated TXT-record `T`-key verification
and corrected discriminator-subtype lookup. Custom harnesses derived from older
scripts need equivalent changes (since sdk-1.5.1.0).

Matter 1.4.1 moved Enhanced Setup Flow and NFC-tag functionality into the
certification program. Public release material does not define cluster IDs,
wire encodings, conformance language, or test vectors; use the authorized
specification and test plan.

An SDK implementation tag can precede the corresponding specification release.
In particular, sdk-1.4.2.0 does not by itself establish normative conformance
to the later specification; certification still depends on that specification
and its test plan.

A Thread Border Router inside a Network Infrastructure Manager must support at
least 150 devices and be certified for Thread 1.4. A Wi-Fi access point must
support 100 simultaneous associations, Extended Sleep, and Proxy ARP/NDP. The
corrected Wi-Fi requirement is Proxy ARP/NDP, not Target Wake Time (since
1.4.2).

