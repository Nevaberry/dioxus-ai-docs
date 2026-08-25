---
name: mollie-knowledge-patch
description: Mollie
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Mollie Knowledge Patch

Use this skill when implementing, reviewing, or debugging Mollie integrations
that touch transfers, settlements, API response values, terminals, rate-limit
handling, generated SDK operations, or Mollie Components.

## When to load this skill

Load this skill for work involving:

- Draft Transfers API requests or state handling.
- Balance-transaction `type` parsing.
- Settlement cost or revenue subtotal `method` parsing.
- Open-settlement or next-settlement convenience responses.
- Mollie locale values or payment-detail card fee regions.
- Terminal pairing-code requests, retrieval, or listing.
- API rate limits and Mollie Web App usage visibility.
- Generated SDK support for payment-method operations.
- Mollie.js v2 Card or Express component types.

## Reference index

| Reference | Topics |
| --- | --- |
| [transfers-and-settlements.md](references/transfers-and-settlements.md) | Draft Transfers requirements, settlement subtotal methods, open and next settlement IDs |
| [api-values.md](references/api-values.md) | Balance-transaction types, locales, and payment-detail card fee regions |
| [terminals-and-api-operations.md](references/terminals-and-api-operations.md) | Terminal pairing-code behavior, rate limits, usage visibility, generated SDK operations |
| [components.md](references/components.md) | Mollie.js v2 Card and Express component type deprecations |

## Apply the patch

1. Identify which Mollie request, response, parser, enum, or component type the
   work touches.
2. Open the matching reference from the index.
3. Preserve the exact literal values in that reference.
4. Preserve whether the guidance is a requirement, a possible response, a
   deprecation, or an announced introduction.
5. Apply every listed condition for the affected operation.

## Breaking and deprecation checks

### Draft Transfers requests

The Draft Transfers API is available again and is generally available.

For Draft Transfers integrations:

- Use `pending-review` instead of `awaiting-initiation`.
- Limit account-holder names to 70 characters.
- Provide valid debtor IBANs.
- Provide valid creditor IBANs.

Do not retain `awaiting-initiation` as the integration value where
`pending-review` is required.

### Mollie Components types

The old `ComponentType` values for Card and Express components in the
private-beta Mollie.js v2 are deprecated.

Those component types are being renamed ahead of public release. Treat the old
Card and Express values as deprecated when working with these private-beta
types.

## Parser and enum quick reference

### Balance transactions

Balance-transaction `type` parsers and enums must accept:

- `application-fee`
- `payment-fee`

The API was already returning both values despite their previous omission from
the documentation.

### Settlement subtotals

The `method` field on settlement cost and revenue subtotals can be:

- `refund`
- `chargeback`

Closed enums for this field must accept both values.

### Locale

The `locale` field accepts:

- `en_BE`
- `en_NL`

### Payment-detail card fee region

Payment-detail card fee-region parsers must accept:

- `visa-credit-consumer-inter`

## Identifier quick reference

### Open settlement

The `id` returned by the open-settlement convenience endpoint is the literal:

- `open`

It is not a normal settlement identifier.

### Next settlement

The `id` returned by the next-settlement convenience endpoint is the literal:

- `next`

It is not a normal settlement identifier.

## Terminal pairing-code behavior

When requesting a terminal pairing code:

- An ineligible organization receives `403`.

For pairing-code retention and lookup:

- Revoked codes are retained for one month.
- Expired codes are retained for one month.
- After permanent deletion, fetching the code returns `404`.
- After permanent deletion, list responses omit the code.

## Rate limits and usage visibility

Mollie is introducing API rate limits and a Mollie Web App section that exposes
usage visibility.

Integrations should:

- Account for the API rate limits.
- Monitor usage in that Mollie Web App section.

## Generated SDK operation support

The profile ID path parameter no longer uses a union schema for operations that
enable or disable:

- Payment methods.
- Payment-method issuers.

This allows all four operations to be generated in language SDKs:

- Enable payment methods.
- Disable payment methods.
- Enable payment-method issuers.
- Disable payment-method issuers.

## Review checklist

When reviewing an affected integration, verify all applicable points:

- Draft Transfer state handling uses `pending-review` rather than
  `awaiting-initiation`.
- Account-holder names are limited to 70 characters.
- Debtor and creditor IBANs are valid.
- Balance-transaction `type` handling accepts `application-fee` and
  `payment-fee`.
- Settlement cost and revenue subtotal `method` handling accepts `refund` and
  `chargeback`.
- Open- and next-settlement response handling accepts the literal IDs `open`
  and `next`.
- Locale handling accepts `en_BE` and `en_NL`.
- Payment-detail card fee-region handling accepts
  `visa-credit-consumer-inter`.
- Terminal pairing-code handling accounts for `403`, one-month retention, and
  post-deletion `404` and list omission.
- The integration accounts for API rate limits and monitors usage in the
  Mollie Web App section.
- SDK generation includes all four enable and disable operations for payment
  methods and payment-method issuers.
- Private-beta Mollie.js v2 Card and Express code treats the old
  `ComponentType` values as deprecated.
