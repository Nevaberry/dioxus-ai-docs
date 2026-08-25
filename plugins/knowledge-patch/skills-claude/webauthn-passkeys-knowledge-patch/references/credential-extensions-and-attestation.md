# Credential Extensions and Attestation

Use this reference when implementing payment assertions, credential-specific
secret derivation, WebAuthn PRF inputs, or make-credential attestation format
selection.

## Third-party payment assertions

The `thirdPartyPayment` extension permits a credential registered by one
relying party to be asserted in a transaction initiated by another relying
party. This is the CTAP primitive for Secure Payment Confirmation.

The extension is not a complete payment workflow. It still needs coordinated
browser or client support, and the surrounding payment flow must supply its
remaining transaction behavior. Treat extension availability as one
capability check, not as proof that end-to-end payment confirmation is ready.

Integration review should distinguish at least:

- the relying party that registered the credential;
- the party initiating the transaction;
- the browser or client exposing the feature; and
- the surrounding payment flow using the assertion.

## Creation-time credential secrets

### Native CTAP

`hmac-secret-mc` makes credential-specific secret derivation available during
`authenticatorMakeCredential`. A native client can obtain the needed result as
part of registration instead of issuing an immediate, separate
`authenticatorGetAssertion` solely for secret derivation.

Keep the extension in the creation path. Do not retain the old extra-assertion
round trip when creation-time support is available and selected.

### WebAuthn PRF mapping

At the WebAuthn layer, the PRF input's `eval` field is the creation-time
counterpart. The similarly named `evalByCredential` field remains
assertion-only.

Model ceremony inputs separately:

| Ceremony | Secret-derivation input |
| --- | --- |
| Credential creation | PRF `eval` at the WebAuthn layer, or `hmac-secret-mc` for native CTAP |
| Assertion | `evalByCredential` when per-credential evaluation is required |

Do not copy an assertion request shape unchanged into registration code.

## Attestation format negotiation

`authenticatorMakeCredential` accepts `attestationFormatsPreference`, an
ordered list of attestation statement formats that the client will accept.
The authenticator chooses its most-preferred supported match from that list.

Pair this input with `getInfo.attestationFormats`:

1. discover the authenticator's supported statement formats;
2. determine which of those formats the client accepts;
3. order the acceptable formats according to client preference; and
4. pass that ordered list as `attestationFormatsPreference`.

This replaces trial-and-error format discovery. Preserve the distinction
between client ordering and authenticator choice: the authenticator selects
its most-preferred supported match, not necessarily the first format the
client would choose without considering authenticator support.

## Review cases

- A payment flow does not activate solely because `thirdPartyPayment` is
  understood by one component.
- Registration-time secret derivation does not trigger an unnecessary
  follow-up assertion.
- Creation code uses `eval`, not `evalByCredential`.
- Assertion code can retain `evalByCredential` where per-credential inputs are
  required.
- Attestation selection uses both the supported-format discovery field and an
  ordered acceptable-format list.
- Failure handling reports that no acceptable supported match exists rather
  than probing formats one at a time.
