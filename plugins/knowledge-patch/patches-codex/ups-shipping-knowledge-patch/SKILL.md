---
name: ups-shipping-knowledge-patch
description: UPS Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# UPS Shipping APIs

Use this skill for current UPS API integration work involving shipping, rating,
tracking, pickup, OAuth, webhooks, international compliance, freight, or
supply-chain services.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migrations and platform](references/migrations-and-platform.md) | Track Alert v2, schema migrations, array consistency, certificates, OAuth, portal security, webhooks, and the UPS MCP server |
| [Shipping, rating, and tracking](references/shipping-rating-and-tracking.md) | Error codes, surcharges, Time in Transit, Roadie, Delivery Intercept, and shipment linkage |
| [Pickup, freight, and supply chain](references/pickup-freight-and-supply-chain.md) | Smart Pickup, Lab Logistics, SCS ingestion, Forwarding, and TradeDirect |
| [International compliance and assurance](references/international-compliance-and-assurance.md) | Delivery tokens, customs, Windsor Lane, tax IDs, Global Checkout, Export Assure, and address confidence |

## Breaking changes and migration priorities

### Track Alert v2

Version 2 of Track Alert and Track Alert with Photo removes the `destination`
object. Clients migrating to v2 must not require or deserialize that object.

Both premium APIs are available globally. Their events include `gmtOffset` in
`(-/+)HH.MM` form to explain local-time conversion.

### Removed and relaxed schema fields

Do not expect these fields on `LabelDelivery_EMail`:

- `UndeliverableEMailAddress`
- `FromEMailAddress`
- `FromName`
- `Memo`
- `Subject`
- `SubjectCode`

`Master_SoldTo.AttentionName` is no longer required.

Pickup creation adds `Notification` and
`PickupCreationRequest_Notification`, and makes `StateProvince` optional.

Open Account adds:

- `RateTypeCode`
- `RateConstructCode`

Track by Reference Number adds:

- `destCountry`
- `destZip`
- `shipperNum`

### Consistent array response paths

Use API versions that consistently return fields documented as arrays:

| Version | APIs |
| --- | --- |
| `v2403` | Shipping, Rating, Pickup, Dangerous Goods Chemical Reference Data |
| `v2` | Dangerous Goods Acceptance Audit Pre-check, Pre Notification, Paperless Documents, Locator, Quantum View, Ship Void, Address Validation, Landed Cost |

Older paths retain inconsistent scalar-or-array behavior for compatibility.

### Locally maintained certificate stores

Clients connecting to `onlinetools.ups.com` with a locally maintained
certificate trust store must follow the DigiCert migration guidance and update
that store.

Browser clients and systems that automatically trust public certificate
authorities need no action.

### Request requirements that can block or warn

- Mexico shipment requests require tax-ID information, matching the existing
  requirement for Indonesia and Vietnam.
- Roadie rating requests require `AddressLine`.
- Windsor Lane shipments require a commercial invoice or the API returns a
  warning.

## OAuth and developer platform quick reference

### Callback registration

Authorization-code callbacks may use localhost. A localhost callback must use
`http://` and include a port.

Supplied `state` and `scope` query parameters are returned to the client.

Enter multiple callback URLs as a comma-separated list with no spaces:

```text
http://localhost:3000/callback,https://shop.example.com/ups/callback
```

### Steppingstone migrations

Use OAuth Steppingstone mode when a migration cannot yet replace SOAP/XML
payloads with REST payloads. It accepts the existing SOAP/XML format while
moving authentication to OAuth 2.0.

### Portal and credential controls

- Accessing API credentials or an application in the Developer Portal prompts
  users to reauthenticate with MFA.
- Commerce Guard and Global Checkout can be requested through the application
  add/edit flow.
- Manage Webhook Credentials configures and maintains webhook credentials
  centrally instead of separately at each integration point.
- UPS provides an MCP server with Track and Address Validation tools for agent
  integrations.

## Shipping, rating, and tracking quick reference

### Expanded known error codes

Error handlers must accept the following as known UPS codes:

| Surface | Codes and changes |
| --- | --- |
| Shipping / Label Recovery | `9801061`, `9801062`, `9801064`, `9801065`, `9801067` |
| Shipping | `120466`; description changed for `120200` |
| Dangerous Goods | `9190048` |
| Pre Notification | `9290059` |

### Fees and transit indicators

- Shipping and Rating recognize surcharge code `573` for the International
  Process Fee.
- Rating can return warning `112259` when the fee is added to a shipment.
- Time in Transit requests accept `premierIndicator` to mark a shipment that
  contains a Premier package.

### Roadie and RoadieXD

Rating versions `2409` or newer return `Zone` for Roadie. Shipping and Rating
also add RoadieXD service types, subtypes, accessorials, and surcharge codes.

### Delivery Intercept

Delivery Intercept supports automated intercept requests. Call its eligibility
endpoint to determine which intercept type is valid before submitting a
request. Add the API through the standard application add/edit flow.

### Master and child shipment linkage

- Create World Ease master and child shipments with the Shipping API,
  including World Ease packages originating in Canada.
- Relate consolidated Worldwide Economy packages to their master carton with
  `MasterCartonID` for cross-level tracking.

## International and delivery quick reference

### Windsor Lane

Shipping supports:

- Northern Ireland-to/from-GB routes where the GB postcode begins `BT`.
- Northern Ireland-to/from-EU routes.

The update adds `ConsgineeTypevalue` and `ShipmentRiskEnteringEU`.

### Choose the compliance or assurance surface

| Need | Surface |
| --- | --- |
| Require a PIN before package release without exposing it directly | Protected Delivery Token |
| Obtain current UPS-shipment compliance requirements before submission | Customs Detail |
| Get guaranteed international duty-and-tax quotes at checkout | Global Checkout GraphQL API |
| Guide goods descriptions and check destination-specific commodity compliance | Export Assure |
| Get a pre-label address-confidence score based on delivery data | DeliveryDefense Address Confidence |

Global Checkout country, province, and measurement-unit codes are defined in a
dedicated appendix.

## Pickup, freight, and supply-chain quick reference

### Smart Pickup choices

- Smart Pickup API triggers Smart Pickups independently of a merchant's
  platform integration.
- Smart Pickup Widget owns authentication, scheduling logic, and UPS API
  communication.
- Pickup Notification Preferences API manages notification settings at the
  account level.
- UPS Lab Logistics Pickup Points lets clinics and laboratories schedule daily
  or date-specific Smart Pickups through a centralized API.

### Freight and ingestion choices

| Need | API |
| --- | --- |
| Create and manage air, ocean, or ground freight-forwarding shipments | Forwarding API |
| Synchronize WMS orders and updates for order and inventory visibility | SCS Inventory |
| Ingest operational events in near real time | SCS Logistics |
| Send TMS shipments and updates to the UPS Supply Chain Symphony datastore | SCS Transportation |
| Ship directly from manufacturers to international end consumers | TradeDirect |

Forwarding shipments can be billed to a shipper, receiver, or third-party
account. The Shipping API can create TradeDirect shipments.
