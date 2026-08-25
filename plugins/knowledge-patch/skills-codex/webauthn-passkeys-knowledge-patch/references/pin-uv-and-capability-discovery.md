# PIN/UV Authorization and Capability Discovery

Use this reference for native credential-management authorization and
authenticator-reported PIN, UV, and attestation capabilities.

## Persistent authorization for enumeration

CTAP 2.2 adds a persistent PIN/UV authorization form that can remain valid
across authenticator power cycles. It is narrower than a general-purpose
authorization token.

The persistent token can authorize only these read-only operations:

| Operation | Purpose |
| --- | --- |
| `enumerateRPs` | Enumerate relying parties with discoverable credentials |
| `enumerateCredentials` | Enumerate credentials for the selected scope |
| `getCredentialMetadata` | Read credential-management metadata |

It cannot authorize an assertion or credential creation. Reject or avoid it
for `authenticatorGetAssertion`, `authenticatorMakeCredential`, and every
operation outside the three permitted reads.

This token complements the session-scoped `cm` token. Choose between them from
the required operation and lifetime rather than treating persistence as a
broader permission.

WebAuthn does not expose persistent PIN/UV authorization. The feature is
therefore primarily for native clients that communicate with authenticators
through CTAP.

## Authenticator PIN and UV discovery

`authenticatorGetInfo` can report these CTAP 2.2 fields:

- `pinComplexityPolicy`;
- the optional `pinComplexityPolicyURL`;
- `maxPINLength`;
- `uvCountSinceLastPinEntry`; and
- supported `attestationFormats`.

Use `pinComplexityPolicy` to detect authenticator-specific policy information
and `pinComplexityPolicyURL` when device-specific guidance should be shown.
Use `maxPINLength` when shaping PIN input validation. The
`uvCountSinceLastPinEntry` field exposes user-verification activity since the
last PIN entry. Use `attestationFormats` during make-credential negotiation as
described in the attestation reference.

## Policy boundary

These fields expose whether device-specific complexity policy information is
active or available. CTAP does not define a universal PIN complexity rule set
and does not require universal policy enforcement.

Consequently, a client should:

1. inspect the reported fields;
2. adapt its PIN validation and rejection guidance to those signals;
3. offer the policy URL when present and useful; and
4. avoid presenting a client-invented rule as a protocol requirement.

Do not infer an authenticator's complete policy from `maxPINLength` alone.

## Native-client review cases

- A persistent token still works after a power cycle for an allowed
  enumeration read.
- The same token is refused for credential creation and assertion.
- Code requiring another credential-management action selects an appropriate
  session-scoped authorization path instead of widening persistent-token
  scope.
- PIN UI handles absent optional policy information.
- Rejection guidance follows the authenticator's reported policy signals.
- WebAuthn browser code does not expect access to the persistent token.
