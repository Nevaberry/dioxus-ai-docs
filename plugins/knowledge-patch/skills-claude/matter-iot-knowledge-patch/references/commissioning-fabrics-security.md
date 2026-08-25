# Commissioning, Fabrics, and Security

Use this reference for onboarding UX, commissioning transports, fabric
administration, credentials, access policy, and certification decisions.

## Setup flows and onboarding payloads

### Enhanced Setup Flow

Enhanced Setup Flow lets a commissioner present localized manufacturer terms,
collect user consent, and return the response to the device. The device may
adjust its functionality based on that response. Commissioners without support
must preserve the pre-existing Custom Commissioning Flow through the
manufacturer's application (1.4.1).

The previously provisional Enhanced Setup Flow and NFC-tag work entered the
certification program in 1.4.1. Public material for that release does not
provide the cluster IDs, wire encodings, conformance language, or test vectors;
use the authorized specification and test plan for implementation and
certification.

### Multipack QR and BLE reads

A single setup QR code may contain onboarding information for multiple devices,
so a compatible commissioner can set up a multipack from one scan (1.4.1).

The SDK adds BLE commissioning APIs for concatenated QR codes, and Darwin
supports BLE connections with multiple discriminators. Commissioners may also
request extra attributes during commissioning; Darwin exposes this through
`MTRCommissioningParameters.readEndpointInformation` (sdk-1.4.2.0).

### Manufacturer terms deadline

General Commissioning adds the provisional `TCUpdateDeadline` attribute. Code
that consumes it must preserve its provisional status rather than presenting it
as settled normative behavior (sdk-1.4.2.0).

### User-directed commissioning display

User-directed commissioning messages include a passcode-display-length field.
Use it to size the commissioning UI for the number of passcode characters the
receiver must present (sdk-1.5.0.0).

### PASE verifier removal

`RendezvousParameters` no longer contains PASE verifier bits. Integrations that
previously populated or read those bits must remove the dependency when moving
to the newer SDK interface (sdk-1.5.0.0).

## NFC commissioning modes

### Onboarding-only tags

An NFC tag can contain the onboarding payload otherwise encoded by the Matter
QR or numeric setup code. This is useful when a printed code will be
inaccessible after installation, but NFC carries onboarding data only and does
not replace the transport that completes commissioning (1.4.1).

### SDK commissioning support

The SDK adds NFC commissioning support to `SetupPayload`,
`IsCommissioningWithoutPower`, and an Android NFC commissioning manager. These
are implementation facilities beyond merely defining the onboarding-payload
format (sdk-1.5.0.0).

An NFC commissioning change was briefly cherry-picked and then reverted before
the later tag. The two changes have no net released behavior, so do not claim
additional NFC capability on the basis of the intermediate cherry-pick
(sdk-1.5.1.0).

### Bidirectional commissioning

Bidirectional NFC can carry the entire commissioning exchange, including before
a device is fully powered. It does not require another transport to finish,
which supports provisioning fixtures and in-wall products before installation
or power-up (1.6).

## Wi-Fi-only commissioning

Wi-Fi-only products can commission with Wi-Fi Unsynchronized Service Discovery
without a Bluetooth LE radio. This path requires a commissioner that also
supports USD commissioning (1.4.2).

When Network Commissioning connects to a new network, the SDK disconnects the
previously connected network first. Applications must tolerate this deliberate
handoff rather than assuming make-before-break behavior (sdk-1.4.2.0).

## Fabric lifecycle and shared administration

### Restoring stored fabrics

A controller can be set up from an already stored fabric without supplying its
NOC chain again (sdk-1.4.2.0).

The SDK also includes an initial Linux `fabric-admin` implementation for
administering Fabric Synchronization (sdk-1.4.2.0).

### Joint Commissioning groundwork

`CommissioningWindowManager` can open a Joint Commissioning Window. Supporting
SDK work includes ICAC CSR generation and issuance, Joint Commissioning Method
cross-signing scaffolding, Joint Fabric status and data-model support, and
Joint Fabric mode through `DeviceInstanceInfoProvider` (sdk-1.5.0.0).

### Joint Fabric administration

Joint Fabric lets multiple controllers share one fabric identity and coordinate
administration through a common datastore. The group consumes one device
fabric-table slot instead of one slot per participating ecosystem. Controllers
must coordinate their state and administrative actions. Public material does
not define the datastore protocol or its failure semantics, so those details
must not be assumed (1.6).

## Credentials and operational security

### PSA-backed credentials

The crypto layer supports PSA-backed SPAKE2+ and can keep persistent ICD server
keys in PSA storage (sdk-1.4.2.0).

### Vendor ID verification

`CHIPCryptoPAL` can generate Vendor ID verification payloads and PEM-encode
them. The Operational Credentials cluster implements Vendor ID verification
and supports signer certificates (sdk-1.4.2.0).

### ICAC handling

The SDK corrects `AddNOC` handling of ICACs. Separately, TC-SC-3.5 accepts a
commissioner DUT without an ICAC in its chain where permitted. Certification
harnesses must not impose an unconditional ICAC requirement
(sdk-1.5.1.0).

### Single-part authenticated encryption

Crypto-provider integrations may use the added single-part AEAD operation for
authenticated encryption or decryption instead of requiring a multipart path
(sdk-1.5.0.0).

## Access policy and privacy

### Access Restriction Lists

Network Infrastructure Manager devices, including routers and access points,
can use Access Restriction Lists to limit sensitive settings and data to
trusted, verified controllers (1.4.2).

### Existence privacy

Writes and commands perform Access Control checks before checking whether the
target exists. This ordering prevents an unauthorized caller from inferring
the presence of a protected target from the response (sdk-1.5.0.0).

## Device-attestation revocation

During commissioning, ecosystems can consult Certificate Revocation Lists to
identify revoked Device Attestation Certificates and warn about or block
affected devices (1.4.2).

Certificate Revocation Lists can later be partitioned into independently
updated portions, allowing the revocation mechanism to scale without replacing
one monolithic list (1.6).

## Commissionable-discovery certification checks

The TC-SC-4.1 and TC-SC-4.3 scripts use updated TXT-record `T`-key verification
and corrected discriminator-subtype lookup. Custom certification harnesses
based on the earlier script behavior need equivalent corrections
(sdk-1.5.1.0).

## Normative and implementation boundaries

The sdk-1.4.2.0 implementation tag predates the public Matter 1.4.2
specification announcement. Its features do not independently establish
normative conformance. Requirements and certification depend on the authorized
specification and test plan.
