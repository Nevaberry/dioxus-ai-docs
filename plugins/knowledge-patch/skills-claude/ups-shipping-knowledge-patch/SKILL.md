---
name: ups-shipping-knowledge-patch
description: UPS Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# UPS Shipping API Knowledge Patch

Use this skill when building, migrating, or reviewing integrations with UPS
shipping, rating, tracking, pickup, customs, delivery, forwarding, or supply
chain APIs.

Keep changes bounded to the documented API surface. Read the reference that
matches the integration task before changing request models, response models,
authentication, certificate handling, or error handling.

## Reference index

| Reference | Topics |
| --- | --- |
| [Client migrations and compatibility](references/client-migrations-and-compatibility.md) | Track Alert v2, consistent arrays, OAuth callbacks and Steppingstone, DigiCert, error codes |
| [Shipping, rating, and shipment linkage](references/shipping-rating-and-linkage.md) | Schema changes, surcharges, Premier, Windsor Lane, Roadie, Mexico tax IDs, World Ease, Worldwide Economy |
| [Pickup and delivery](references/pickup-and-delivery.md) | Smart Pickup, Lab Logistics pickup points, protected delivery tokens, Delivery Intercept |
| [International and supply chain](references/international-and-supply-chain.md) | Customs Detail, SCS ingestion, Forwarding, TradeDirect, Global Checkout, export and address assurance |
| [Portal, webhooks, and agent integrations](references/portal-webhooks-and-agents.md) | Central webhook credentials, portal MFA and onboarding, UPS MCP server |

## Quick reference: breaking changes and migrations

### Track Alert v2

- Version 2 of Track Alert and Track Alert with Photo removes the
  `destination` object.
- Migrating clients must not require or deserialize `destination`.
- Their events include `gmtOffset` in `(-/+)HH.MM` form to explain local-time
  conversion.

See
[Client migrations and compatibility](references/client-migrations-and-compatibility.md#track-alert-v2).

### Consistent array response versions

Use `v2403` when fields documented as arrays must consistently return arrays
for:

- Shipping
- Rating
- Pickup
- Dangerous Goods Chemical Reference Data

Use `v2` for:

- Dangerous Goods Acceptance Audit Pre-check
- Pre Notification
- Paperless Documents
- Locator
- Quantum View
- Ship Void
- Address Validation
- Landed Cost

Older paths retain inconsistent scalar-or-array behavior for compatibility.

See
[Client migrations and compatibility](references/client-migrations-and-compatibility.md#consistent-array-responses).

### Removed and relaxed schema fields

`LabelDelivery_EMail` no longer has:

- `UndeliverableEMailAddress`
- `FromEMailAddress`
- `FromName`
- `Memo`
- `Subject`
- `SubjectCode`

`Master_SoldTo.AttentionName` is no longer required. Pickup creation makes
`StateProvince` optional.

See
[Shipping, rating, and shipment linkage](references/shipping-rating-and-linkage.md#shipping-pickup-account-and-tracking-schema-changes).

### Newly required shipment inputs

- Roadie rating requests require `AddressLine`.
- Mexico shipment requests require tax-ID information, matching the existing
  requirement for Indonesia and Vietnam.
- Windsor Lane shipments require a commercial invoice or the API returns a
  warning.

See
[Shipping, rating, and shipment linkage](references/shipping-rating-and-linkage.md#required-request-data).

### OAuth and trust-store migration

- A localhost authorization-code callback must use `http://` and include a
  port.
- Enter multiple callback URLs as a comma-separated list with no spaces.
- Steppingstone accepts existing SOAP/XML payloads while authentication moves
  to OAuth 2.0.
- Clients connecting to `onlinetools.ups.com` with a locally maintained trust
  store must follow the DigiCert migration guidance and update that store.

See
[Client migrations and compatibility](references/client-migrations-and-compatibility.md#oauth-callback-registration)
and
[Client migrations and compatibility](references/client-migrations-and-compatibility.md#digicert-trust-store-migration).

## Quick reference: API and workflow additions

### Pickup workflows

- The Smart Pickup API can trigger Smart Pickups independently of a
  merchant's platform integration.
- The embeddable Smart Pickup Widget owns authentication, scheduling logic,
  and UPS API communication.
- Pickup Notification Preferences manages notification settings at account
  level.
- UPS Lab Logistics Pickup Points lets clinics and laboratories schedule daily
  or date-specific Smart Pickups through a centralized API.

See
[Pickup and delivery](references/pickup-and-delivery.md#smart-pickup-surfaces).

### Delivery controls

- Protected Delivery Token tokenizes a shipper-generated PIN and lets the
  shipper require that PIN before package release.
- Delivery Intercept automates intercept requests and provides an eligibility
  endpoint for determining the valid intercept type before submission.

See
[Pickup and delivery](references/pickup-and-delivery.md#delivery-controls).

### International checkout and compliance

- Customs Detail supplies current UPS-shipment compliance requirements before
  customs data is submitted.
- Global Checkout is a GraphQL API for guaranteed international duty-and-tax
  quotes at checkout.
- Export Assure provides interactive description-of-goods guidance and
  destination-specific commodity compliance checks.

See
[International and supply chain](references/international-and-supply-chain.md#customs-and-compliance).

### Freight and supply chain

- Forwarding creates and manages air, ocean, and ground freight-forwarding
  shipments.
- SCS Inventory synchronizes WMS orders and updates for order and inventory
  visibility; SCS Logistics ingests operational events in near real time; SCS
  Transportation sends TMS shipments and updates to the UPS Supply Chain
  Symphony datastore.
- TradeDirect supports direct international shipping from manufacturers to end
  consumers, with shipment creation through the Shipping API.

See
[International and supply chain](references/international-and-supply-chain.md#freight-and-supply-chain-apis).

### Integration administration

- Manage Webhook Credentials centralizes webhook credential configuration and
  maintenance.
- Accessing API credentials or an application in the Developer Portal prompts
  reauthentication with MFA.
- The UPS MCP server exposes Track and Address Validation tools for agent
  integrations.

See
[Portal, webhooks, and agent integrations](references/portal-webhooks-and-agents.md).

## Task routing

Use the references as follows:

1. For a client or authentication migration, start with
   [Client migrations and compatibility](references/client-migrations-and-compatibility.md).
2. For request or response model changes in Shipping or Rating, use
   [Shipping, rating, and shipment linkage](references/shipping-rating-and-linkage.md).
3. For pickup, release, intercept, or tracking behavior, use
   [Pickup and delivery](references/pickup-and-delivery.md).
4. For customs, international checkout, freight, or supply chain ingestion,
   use
   [International and supply chain](references/international-and-supply-chain.md).
5. For portal access, webhooks, or agent tools, use
   [Portal, webhooks, and agent integrations](references/portal-webhooks-and-agents.md).
