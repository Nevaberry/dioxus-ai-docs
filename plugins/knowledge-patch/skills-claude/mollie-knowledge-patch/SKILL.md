---
name: mollie-knowledge-patch
description: Mollie
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Mollie Knowledge Patch

Use this skill when implementing, reviewing, or updating Mollie integrations,
API response models, generated SDKs, terminal pairing flows, settlement logic,
or Mollie Components types.

Keep enum handling open to every value documented here. Preserve the exact
literal identifiers and status values described by this patch.

## Reference index

| Reference | Topics |
| --- | --- |
| [transfers-and-settlements.md](references/transfers-and-settlements.md) | Draft Transfers requirements, settlement subtotal methods, and open/next settlement identifiers |
| [api-values-and-terminals.md](references/api-values-and-terminals.md) | Balance-transaction values, locales, card fee regions, terminal pairing-code behavior, and rate-limit visibility |
| [sdk-and-components.md](references/sdk-and-components.md) | Generated payment-method operations and Mollie Components type deprecations |

## Apply compatibility changes first

### Retire deprecated Mollie Components types

The old `ComponentType` values for Card and Express components in the
private-beta Mollie.js v2 are deprecated. Those component types are being
renamed ahead of public release.

Treat the old Card and Express values as deprecated. Do not invent replacement
names from this guidance; it does not provide the new names.

See [sdk-and-components.md](references/sdk-and-components.md) for the exact
scope of the deprecation.

### Update Draft Transfers requests

The Draft Transfers API is available again and is generally available.

For Draft Transfers integrations:

- use `pending-review` instead of `awaiting-initiation`;
- limit account-holder names to 70 characters;
- provide a valid debtor IBAN; and
- provide a valid creditor IBAN.

Apply all four requirements together when updating a request path. See
[transfers-and-settlements.md](references/transfers-and-settlements.md).

### Expand closed API enums

Do not reject these values in parsers or closed enums:

| Field or context | Values to accept |
| --- | --- |
| Balance-transaction `type` | `application-fee`, `payment-fee` |
| Settlement cost subtotal `method` | `refund`, `chargeback` |
| Settlement revenue subtotal `method` | `refund`, `chargeback` |
| `locale` | `en_BE`, `en_NL` |
| Payment-detail card fee region | `visa-credit-consumer-inter` |

The balance-transaction API was already returning `application-fee` and
`payment-fee` even though they had been omitted from the documentation.

Read [api-values-and-terminals.md](references/api-values-and-terminals.md) for
balance transactions, locales, and card fee regions. Read
[transfers-and-settlements.md](references/transfers-and-settlements.md) for
settlement subtotal methods.

## Preserve special settlement identifiers

The `id` returned by the open-settlement convenience endpoint is the literal
`open`.

The `id` returned by the next-settlement convenience endpoint is the literal
`next`.

Neither value is a normal settlement identifier. Models and validators for
these convenience endpoints must therefore preserve their respective literal
value rather than require a normal settlement identifier.

See [transfers-and-settlements.md](references/transfers-and-settlements.md).

## Handle terminal pairing-code outcomes

Requesting a terminal pairing code returns `403` when the organization is
ineligible.

Revoked and expired pairing codes are retained for one month.

After a pairing code is permanently deleted:

- fetching it returns `404`; and
- list responses omit it.

Keep the one-month retained state distinct from permanent deletion when
handling fetch and list results.

See [api-values-and-terminals.md](references/api-values-and-terminals.md).

## Account for API limits and usage visibility

Mollie is introducing API rate limits. Integrations should account for those
limits.

Mollie is also introducing a Mollie Web App section that exposes usage
visibility. Integrations should monitor their usage there.

Do not turn this guidance into a specific numeric limit; no numeric limit is
provided here.

See [api-values-and-terminals.md](references/api-values-and-terminals.md).

## Generate payment-method operations

The profile ID path parameter no longer uses a union schema for operations
that enable or disable payment methods and payment-method issuers.

This change allows all four operations to be generated in language SDKs.

When reviewing generated SDK coverage, include the enable and disable
operations for both payment methods and payment-method issuers.

See [sdk-and-components.md](references/sdk-and-components.md).

## Review checklist

### Request construction

- Draft Transfers use `pending-review`, not `awaiting-initiation`.
- Account-holder names do not exceed 70 characters.
- Debtor and creditor IBANs are valid.

### Response parsing

- Balance-transaction `type` accepts both added fee values.
- Settlement cost and revenue subtotal `method` accepts `refund` and
  `chargeback`.
- Locale handling accepts `en_BE` and `en_NL`.
- Card fee-region handling accepts `visa-credit-consumer-inter`.
- Open and next settlement endpoints preserve `open` and `next` as their
  respective `id` values.

### Terminal behavior

- An ineligible organization can receive `403` when requesting a pairing
  code.
- Revoked and expired codes remain retained for one month.
- Permanently deleted codes return `404` on fetch and disappear from lists.

### SDK and web integration

- Generated SDKs include all four enable/disable operations for payment
  methods and payment-method issuers.
- Old Card and Express `ComponentType` values in private-beta Mollie.js v2 are
  treated as deprecated.
- Integrations account for Mollie API rate limits.
- Usage is monitored in the Mollie Web App section that exposes usage
  visibility.

## Scope discipline

Use the exact values and behaviors above. Where this patch does not state a
replacement name, numeric limit, or additional response behavior, leave that
detail unspecified rather than deriving it from adjacent API behavior.

Open the topic reference before changing code in that area; the references
separate request rules, response values, endpoint lifecycle behavior, and SDK
or component changes.
