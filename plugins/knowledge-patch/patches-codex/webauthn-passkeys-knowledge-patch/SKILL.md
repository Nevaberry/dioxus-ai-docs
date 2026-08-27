---
name: webauthn-passkeys-knowledge-patch
description: WebAuthn / Passkeys
version: null
license: MIT
metadata:
  author: Nevaberry
---


# WebAuthn and Passkeys

Use this skill when implementing or reviewing WebAuthn, passkeys, native CTAP
clients, authenticator capability discovery, credential extensions, attestation
selection, or hybrid authenticator flows.

First identify the API surface in use. A browser-facing WebAuthn application,
a native CTAP client, an authenticator, and an operating-system transport layer
do not expose the same controls. Detect individual capabilities instead of
assuming that a protocol label makes every related feature available.

## How to apply this skill

1. Classify the component as WebAuthn JavaScript, native CTAP, authenticator
   firmware, browser or operating-system transport, or payment integration.
2. Read the compatibility boundaries before mapping a CTAP feature into a web
   application.
3. Discover authenticator fields and extensions individually.
4. Keep authorization tokens within their defined operation and lifetime
   scope.
5. Keep credential-creation inputs separate from assertion-only inputs.
6. Treat hybrid transport and payment primitives as building blocks whose
   complete flows require support from other components.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/pin-uv-and-capability-discovery.md](references/pin-uv-and-capability-discovery.md) | Persistent PIN/UV authorization, credential enumeration, PIN-policy fields, authenticator discovery |
| [references/credential-extensions-and-attestation.md](references/credential-extensions-and-attestation.md) | Third-party payment assertions, creation-time HMAC secrets, WebAuthn PRF phase rules, attestation format negotiation |
| [references/hybrid-transport-and-specification-boundaries.md](references/hybrid-transport-and-specification-boundaries.md) | QR and BLE hybrid setup, encrypted tunnels, WebSocket and BLE data channels, Digital Credentials JSON, CTAP/WebAuthn and certification boundaries |

## Compatibility and exposure boundaries

### Detect capabilities, not a CTAP 2.2 version value

Do not look for `FIDO_2_2` in `authenticatorGetInfo`; that value does not
exist. Probe the specific fields, options, extensions, or handshake
capabilities needed by the implementation.

There is also no separate CTAP 2.2 certification category. Certification uses
the backwards-compatible CTAP 2.3 profile, so certification status is not a
substitute for runtime capability discovery.

### Keep CTAP and WebAuthn claims separate

CTAP and W3C WebAuthn are complementary specifications. A capability defined
for native authenticator communication does not by itself:

- establish the normative status of WebAuthn Level 3;
- guarantee exposure through the WebAuthn JavaScript API; or
- prove that the active browser, operating system, and authenticator support
  the complete flow.

Document which layer owns each feature and test the actual integration path.

## PIN/UV authorization and discovery

### Restrict persistent authorization to enumeration

CTAP 2.2 persistent PIN/UV authorization tokens can survive authenticator
power cycles. Their scope is deliberately read-only and limited to:

- `enumerateRPs`;
- `enumerateCredentials`; and
- `getCredentialMetadata`.

They cannot authorize credential creation or assertions. Do not reuse one for
`authenticatorMakeCredential`, `authenticatorGetAssertion`, or any operation
outside the three credential-management reads.

Persistent tokens complement session-scoped `cm` tokens; they do not replace
all credential-management authorization. WebAuthn does not expose the
persistent form, so it is primarily relevant to native CTAP clients.

### Read PIN-policy signals from `authenticatorGetInfo`

Capability discovery can report:

| Field | Use |
| --- | --- |
| `pinComplexityPolicy` | Detect authenticator-specific PIN complexity policy information |
| `pinComplexityPolicyURL` | Offer the optional device-specific policy guidance URL |
| `maxPINLength` | Shape client-side maximum-length handling |
| `uvCountSinceLastPinEntry` | Observe user-verification activity since the last PIN entry |
| `attestationFormats` | Discover supported attestation statement formats |

The protocol does not define one universal complexity rule set and does not
require every authenticator to enforce such a set. Use the reported fields to
shape validation and rejection guidance without inventing a universal PIN
policy.

## Credential extensions and attestation

### Choose the HMAC-secret input for the ceremony phase

For native CTAP credential creation, `hmac-secret-mc` derives a
credential-specific secret during `authenticatorMakeCredential`. This avoids
performing a separate `authenticatorGetAssertion` immediately after
registration merely to derive the secret.

At the WebAuthn layer, the PRF input `eval` is the creation-time counterpart.
`evalByCredential` remains assertion-only; do not send or model it as a
credential-creation input.

### Treat third-party payment as a primitive

The `thirdPartyPayment` extension allows a credential registered by one
relying party to be asserted when another party initiates the transaction. It
is the CTAP primitive used for Secure Payment Confirmation.

It is not a complete payment flow. Confirm coordinated browser or client
support and keep the surrounding payment protocol responsible for its own
transaction logic and checks.

### Negotiate attestation formats explicitly

`authenticatorMakeCredential` can send
`attestationFormatsPreference`, an ordered list of acceptable attestation
statement formats. The authenticator selects its most-preferred supported
match.

Use `getInfo.attestationFormats` to learn supported formats, then construct the
ordered preference list. This avoids trial-and-error discovery while
preserving both client acceptability and authenticator preference.

## Hybrid transport

### Assign transport ownership correctly

Hybrid flows combine QR initiation, BLE proximity pairing, and an encrypted
network tunnel. Browsers and operating systems implement this transport;
roaming-authenticator SDKs should not assume that they own the entire hybrid
stack.

For QR-initiated flows, CTAP 2.2 uses WebSocket tunnels as the data channel.
CTAP 2.3 adds BLE as an alternative data channel. Do not describe the later
BLE data channel as if it replaced the BLE proximity role in the earlier
flow.

### Keep JSON hybrid messages distinct from direct CTAP

CTAP 2.2 supports JSON-formatted Digital Credentials API messages over hybrid
transport. The hybrid handshake advertises this with the `dc` capability.

Direct CTAP communication continues to use CBOR. Negotiate the hybrid
capability before sending Digital Credentials JSON, and do not generalize that
JSON encoding to direct authenticator commands.

## Implementation workflow

### 1. Identify the caller and ceremony

Record whether the caller is browser JavaScript or a native CTAP client, and
whether the operation is discovery, credential creation, assertion, or
credential-management enumeration.

### 2. Discover only what the operation needs

Probe the relevant `getInfo` fields, make-credential options, extensions, or
hybrid handshake capabilities. Missing capabilities should produce a clear
fallback or unsupported result rather than a guessed protocol-version branch.

### 3. Enforce phase and scope boundaries

- Limit persistent PIN/UV tokens to the three read-only enumeration actions.
- Use `hmac-secret-mc` or PRF `eval` for creation-time derivation.
- Reserve `evalByCredential` for assertions.
- Use `thirdPartyPayment` only within a coordinated payment flow.

### 4. Negotiate rather than probe by failure

Read `getInfo.attestationFormats` before sending an ordered
`attestationFormatsPreference`. Read PIN-policy fields before composing PIN
validation and rejection guidance.

### 5. Test the owning layers together

For hybrid and payment behavior, test the browser or client, operating system,
authenticator, relying parties, and surrounding protocol components that
participate in the chosen flow.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Checking `FIDO_2_2` | Detect each required CTAP 2.2 capability |
| Treating certification as feature detection | Test fields, options, extensions, and handshake capabilities at runtime |
| Using a persistent token for creation or assertion | Restrict it to `enumerateRPs`, `enumerateCredentials`, and `getCredentialMetadata` |
| Applying one universal PIN-complexity policy | Follow authenticator-reported policy signals and device guidance |
| Sending `evalByCredential` during registration | Use creation-time `eval`; keep `evalByCredential` assertion-only |
| Treating `thirdPartyPayment` as the payment protocol | Integrate it as the CTAP primitive within a coordinated flow |
| Encoding direct CTAP commands as JSON | Keep direct CTAP in CBOR; JSON here is negotiated Digital Credentials traffic over hybrid transport |
| Implementing hybrid entirely in a roaming SDK | Account for browser and operating-system ownership |

## Review checklist

- The code identifies its API surface and does not assume native CTAP features
  are available to WebAuthn JavaScript.
- Capability checks target individual fields and options rather than a
  nonexistent `FIDO_2_2` value.
- Persistent authorization is accepted only for the three permitted read-only
  credential-management operations.
- PIN rejection guidance is derived from authenticator signals without
  claiming a universal protocol-defined complexity rule.
- Creation-time secret derivation uses the creation input, while
  per-credential assertion inputs stay in the assertion path.
- Third-party payment assertions are gated on coordinated client support.
- Attestation preferences are ordered and intersect known authenticator
  support.
- Hybrid JSON is gated by `dc`, while direct CTAP remains CBOR.
- Tests cover the browser or operating-system transport layer for hybrid
  behavior.
- Documentation does not infer WebAuthn Level 3 status or JavaScript exposure
  solely from CTAP behavior.
