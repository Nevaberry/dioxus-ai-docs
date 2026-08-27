# Hybrid Transport and Specification Boundaries

Use this reference for hybrid authenticator architecture, data-channel and
message encoding decisions, capability negotiation, and CTAP/WebAuthn version
or certification claims.

## Hybrid flow architecture

Hybrid flows combine three distinct pieces:

1. QR initiation;
2. BLE proximity pairing; and
3. an encrypted network tunnel.

Browsers and operating systems implement this transport. A
roaming-authenticator SDK should integrate with that ownership boundary rather
than attempting to implement or expose the full browser/OS transport itself.

## Data channels

For QR-initiated flows, CTAP 2.2 uses WebSocket tunnels as the data channel.
CTAP 2.3 adds BLE as an alternative data channel.

Keep the roles distinct: BLE proximity pairing is part of the hybrid setup,
while the CTAP 2.3 addition allows BLE to serve as an alternative data channel.
The later option does not make every CTAP 2.2 hybrid implementation a BLE data
channel implementation.

## Digital Credentials messages

CTAP 2.2 adds JSON-formatted Digital Credentials API messages over hybrid
transport. A peer advertises this support through the `dc` hybrid-handshake
capability.

Only select that message path when the handshake advertises `dc`. Direct CTAP
communication continues to use CBOR, so the presence of a JSON format in the
hybrid path does not change direct authenticator-command encoding.

| Path | Message or channel rule |
| --- | --- |
| QR-initiated CTAP 2.2 hybrid | WebSocket tunnel data channel |
| CTAP 2.3 hybrid alternative | BLE may be the data channel |
| Digital Credentials over hybrid | JSON after `dc` capability negotiation |
| Direct CTAP | CBOR |

## Capability and certification detection

There is no `FIDO_2_2` value in `authenticatorGetInfo`. Code must detect the
individual CTAP 2.2 fields and capabilities that it needs.

There is likewise no separate CTAP 2.2 certification category. Certification
targets the backwards-compatible CTAP 2.3 profile. Do not translate a
certification label into an assumed `FIDO_2_2` value or skip runtime feature
detection because a device has been certified.

## CTAP and WebAuthn separation

CTAP and W3C WebAuthn are complementary specifications with different
interfaces and responsibilities. CTAP 2.2 material alone does not:

- establish whether WebAuthn Level 3 is normative;
- guarantee that a browser exposes a corresponding WebAuthn JavaScript API;
  or
- guarantee support by the browser, operating system, client, and
  authenticator needed for an end-to-end flow.

When documenting or reviewing an integration, attribute each capability to
its actual layer. Feature-detect the native CTAP behavior, then separately
verify any browser or operating-system exposure required by the application.

## Review cases

- A QR-initiated CTAP 2.2 flow uses its WebSocket tunnel and does not assume
  the later BLE data-channel option.
- BLE proximity setup and BLE data transport are represented as distinct
  roles.
- Digital Credentials JSON is sent only after `dc` negotiation.
- Direct CTAP remains CBOR encoded.
- The roaming-authenticator component does not claim ownership of browser or
  operating-system transport behavior.
- Capability discovery never checks for `FIDO_2_2`.
- Certification does not replace field-level runtime checks.
- Documentation avoids inferring WebAuthn Level 3 status or JavaScript API
  exposure from CTAP 2.2 alone.
