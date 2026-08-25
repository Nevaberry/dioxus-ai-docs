---
name: dhl-shipping-knowledge-patch
description: DHL Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# DHL Shipping API compatibility

Load this skill when implementing, migrating, or reviewing integrations with
DHL eCommerce Americas v4, DHL Location Finder, MyDHL API, or Parcel Germany
Shipping v2. Identify the product first: their authentication, environments,
account rules, resources, service identifiers, and data-use terms differ.

## Reference index

| Reference | Topics |
|---|---|
| [Access and operations](references/access-and-operations.md) | Product scope, authentication, environments, quotas, compatibility, migration, and usage restrictions |
| [Discovery and locations](references/discovery-and-locations.md) | Product Finder, Location Finder searches and filters, service identifiers, response fields, and shipment addressing |
| [Shipment, labels, and manifests](references/shipment-labels-and-manifests.md) | Shipment inputs, pickup, labels, closeout, returns, lifecycle, and Parcel Germany response behavior |
| [Customs, rating, and dangerous goods](references/customs-rating-and-dangerous-goods.md) | International rules, rates, landed cost, customs codes, invoice data, and dangerous goods |
| [Tracking and documents](references/tracking-and-documents.md) | Tracking fields, image types, invoice upload, piece-to-label linkage, and document retrieval |

## Breaking changes, retirements, and deadlines

### Retired Location Search Europe

Location Search Europe is decommissioned. Migrate to Unified Location Finder
v1 and apply the documented response mappings. Several legacy fields have no
Unified equivalent; see [Discovery and locations](references/discovery-and-locations.md).

### Parcel Germany transport and schema changes

- Parcel Germany REST v2 remains active. GKV SOAP 1.x and 2.x are retired,
  and GKV SOAP 3.x reached its stated sunset on May 31, 2026.
- OAuth 2 uses the separately assigned Post & Parcel Germany Authentication
  API. Basic Auth with `dhl-api-key` remains a v2 alternative but is slated
  for removal in a future major version.
- `officeOfOrigin` is deprecated. Follow the corrected `GET /labels`,
  `GET /manifests`, `shippingConditions`, and `product` schemas.
- DHL Kleinpaket replaced Warenpost on January 1, 2025. Kleinpaket now
  requires `Consignee.ContactAddress.country` as an ISO 3166-1 alpha-3 code.

### MyDHL cutoff-field migration

Versioned Shipment and Rates responses expose
`pickupCutoffSameDayOutboundProcessing` through `x-version` as the replacement
for `GMTCutoffTime`. Consumers should migrate field handling rather than
treating the two names as unrelated cutoff values.

### GoGreen label deadlines

- Remove the GoGreen logo by August 31, 2026, when GoGreen ends.
- Remove the existing GoGreen Plus logo by September 27, 2026.
- The new GoGreen Plus claim is optional. The service remains available for
  national outbound and return shipments.

## Choose the correct API

| Product | Supported integration scope |
|---|---|
| eCommerce Americas v4 | Discovery, duty and tax calculation, labels, manifests, tracking, and returns for domestic and international packages originating in the United States or Canada |
| Location Finder v1 | GET-only lookup by address, coordinates, location ID, or `keywordId` |
| MyDHL API | DHL Express product/rating, shipment, pickup, tracking, invoice, image, reference-data, and service-point operations for an active DHL Express customer account |
| Parcel Germany Shipping v2 | Labels and export documents for goods shipments originating in Germany for eligible Post & Parcel Germany business customers |

MyDHL Service Point should not be substituted for another DHL division's
location API. Its contract is specific to MyDHL.

## Authentication and environment quick reference

### eCommerce Americas

- Test at `https://api-sandbox.dhlecs.com`; use
  `https://api.dhlecs.com` in production.
- Labels and manifests do not cross environments. Verify production pickup
  access, products, capacity, account data, distribution centers, and allowed
  content categories separately.
- Network allowlists and TLS policy should be checked against the
  inbound/outbound IPs and supported TLS cipher versions published effective
  August 18, 2026.

### Location Finder

- Call `https://api.dhl.com/location-finder/v1` with an approved app key in
  `DHL-API-Key`.
- New access starts at 500 calls per day. Exhaustion returns HTTP `429`; an
  app upgrade request is required for a higher limit.

### MyDHL API

- Use pre-emptive HTTP Basic authentication with issued credentials.
- Test at `https://express.api.dhl.com/mydhlapi/test`; production is
  `https://express.api.dhl.com/mydhlapi`.
- Test credentials allow 500 service invocations per day.

### Parcel Germany Shipping v2

- Obtain an OAuth 2 access token by sending the portal username/password and
  app key/secret to the Post & Parcel Germany Authentication API, then use
  `Authorization: Bearer ...`.
- A production integration should use a non-interactive system user. Its portal
  password expires after 365 days; a personal user's expires after 90 days.
- A new API key may not work until 00:00 CEST.
- Test at `https://api-sandbox.dhl.com/parcel/de/shipping/v2/`; production is
  `https://api-eu.dhl.com/parcel/de/shipping/v2/` and requires approval after
  successful sandbox use.

## Compatibility and failure handling

### eCommerce Americas clients

Within an API version, tolerate new optional request/query fields, added
response fields, property reordering, new methods, and new resources. Use
product codes, error codes, and event IDs as integration keys instead of
mutable names or descriptions.

Error details are linked at
`https://api.dhlecs.com/docs/errors/<error-code>`. Handle both independent
`429` cases with queue-and-retry behavior: per-resource parallel-request Spike
Arrest and account-specific weekly cross-resource Quota Violation.

### MyDHL validation flow

Use `Product` for lightweight one-piece capability lookup. `Rating` adds
account rates, value-added services, and estimated delivery. DHL recommends
rating before shipment creation so only eligible products and services are
submitted.

Requests undergo schema/cardinality validation and then business-rule
validation; findings appear in the operation result message. JSON must not
begin with a byte-order mark.

### Parcel Germany request and warning behavior

- `POST /orders` and other array operations return entries in request order;
  even one request entry receives a one-entry response array.
- Use `validate=true` to validate fields and business rules without creating
  a shipment.
- Warning responses do not invalidate an accompanying label. Use
  `mustEncode=true` if label creation must require an encodable street.
- Omit a missing consignee phone or email, or send `null`; do not send
  whitespace.

## High-value shipment rules

### eCommerce Americas

- `PLX` is DHL Parcel International Expedited and does not support dangerous
  goods.
- Domestic-label `customsDetails` is only for APO, FPO, DPO, and
  non-continental US destinations; it should be omitted elsewhere.
- Use Manifest `products` to close out packages by selected product.
- Put optional `deliveryInstructions` in `consigneeAddress`.

### MyDHL API

- Since version 3.3.0, pickup validation and Rates pickup capabilities use the
  shipper account number's cutoff, not only the origin or a generic schedule.
- A standardized packaging type code lets Rating and Shipment populate
  dimensions. `addPiece` works only before pickup or a recorded scan.
- Package dimensions must be positive and greater than `0.001`.
- Validate shipment data without creating a label when needed.

### Parcel Germany Shipping v2

- One physical parcel is one shipment; multipackage shipments are unsupported.
- The 14-character `billingNumber` combines the ten-digit EKP, two-character
  procedure/product, and participation. Support multiple billing numbers or
  participations.
- Created shipments can be canceled and recreated only until manifested.
  Manifested shipments cannot be changed.
- International parcels must be manifested before handoff.
- Do not scale labels; thermal formats assume 203 dpi.

## High-value discovery rules

- Location Finder repeats of `serviceType` are AND conditions.
  `parcel:pick-up-all` and `parcel:drop-off-all` are query-only family
  meta-services and are not returned as service values.
- Use `providerType=parcel` to exclude Express locations.
- A syntactically valid but uncovered country can return `200` with no
  locations; an invalid country code returns `400`.
- Direct shipment addressing is not for DHL Express and requires a location
  with a designated Postfiliale number in `keywordId`. Supply the recipient's
  email for pickup notification.
- Location Data must not be stored or modified. Its display and analysis terms
  are detailed in [Access and operations](references/access-and-operations.md).

## High-value customs and document rules

- For eCommerce Americas PLT dangerous-goods categories `01`–`06` and `40`,
  allow Canada and Mexico and reject other destinations.
- MyDHL declarable non-document shipments require `exportDeclaration`.
  Monetary, weight, duty, tax, and additional-charge values must be positive.
- Parcel Germany customs data is per parcel outside the applicable customs
  union. UK `BT` postcodes are treated as Northern Ireland/EU and need no
  customs data.
- MyDHL protected tracking data is masked and requires authorization.
- A MyDHL Customs Entry Document image requires the requester to be the
  Exporter of Record.

Use the indexed references for the complete field, code, eligibility,
rendering, retention, and lifecycle rules.
