---
name: dhl-shipping-knowledge-patch
description: DHL Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# DHL Shipping API Guidance

Use this skill when selecting, implementing, reviewing, or migrating among the DHL eCommerce Americas, DHL Location Finder, MyDHL Express, and Parcel Germany Shipping APIs. Identify the DHL division and contract before choosing endpoints, credentials, product codes, location services, or shipment rules.

## Reference index

| Reference | Topics |
| --- | --- |
| [API selection and access](references/api-selection-and-access.md) | Product scope, accounts, authentication, environments, quotas, endpoints, compatibility |
| [Location search and addressing](references/location-search-and-addressing.md) | Search modes, filters, location and service identifiers, response data, direct addressing, migration |
| [Shipment, label, and manifest lifecycle](references/shipment-label-and-manifest.md) | Shipment inputs, labels, manifests, pickup behavior, returns, rendering, schema changes |
| [Customs and dangerous goods](references/customs-and-dangerous-goods.md) | Customs details, product restrictions, registrations, reference and document codes, dangerous goods |
| [Rates, tracking, images, and reference data](references/rates-tracking-and-documents.md) | Rating, landed cost, cutoff fields, tracking, document images, invoice totals, reference datasets |

## Breaking changes and retirements

### Retired location and shipping APIs

- Location Search Europe is decommissioned. Migrate to Unified Location Finder v1, using the documented field mappings and accounting for fields with no Unified equivalent.
- Parcel Germany GKV SOAP 1.x and 2.x are retired. GKV SOAP 3.x reached its stated sunset on May 31, 2026; use REST Shipping v2.

### Authentication migration

Parcel Germany Shipping v2 supports OAuth 2 through the separately assigned Post & Parcel Germany Authentication API. Basic Auth with `dhl-api-key` remains an alternative in v2 but is slated for removal in a future major version.

### Renamed and deprecated fields

- Versioned MyDHL Shipment and Rates responses introduced `pickupCutoffSameDayOutboundProcessing` through `x-version` as the replacement for `GMTCutoffTime`. Migrate field handling rather than treating the names as independent cutoff values.
- Parcel Germany `officeOfOrigin` is deprecated.
- Parcel Germany clients should follow the corrected `GET /labels`, `GET /manifests`, `shippingConditions`, and `product` schemas.

### GoGreen label deadlines

- GoGreen ends on August 31, 2026, and its logo must be removed by that date.
- Remove the existing GoGreen Plus logo by September 27, 2026. A new GoGreen Plus claim is optional; the service remains available for national outbound and return shipments.

## Choose the correct contract

| Contract | Supported use |
| --- | --- |
| eCommerce Americas v4 | Product discovery, duties and taxes, labels, manifests, tracking, and returns for domestic and international packages originating in the United States or Canada |
| Location Finder v1 | GET-only lookup by address, coordinates, location ID, or `keywordId` |
| MyDHL API | DHL Express product, rating, shipment, pickup, tracking, image, invoice, landed-cost, reference-data, and service-point operations |
| Parcel Germany Shipping v2 | Labels and export documents for goods shipments originating in Germany, domestically or internationally |

Do not substitute the MyDHL Service Point contract for another DHL division's location API. Its operation is specific to MyDHL and finds Express points from a postal address, service-point ID, or geocode.

## Access and environment quick reference

### eCommerce Americas

- Test against `https://api-sandbox.dhlecs.com`; use `https://api.dhlecs.com` in production.
- Labels and manifests do not cross environments.
- Verify production pickup access, products, capacity, account master data, distribution centers, and allowed content categories separately before launch.
- Check network allowlists and TLS policy against the inbound and outbound IP addresses and cipher versions published effective August 18, 2026.

### Location Finder

- Production base URL: `https://api.dhl.com/location-finder/v1`.
- Every call requires an approved app key in `DHL-API-Key`.
- Initial access is 500 calls per day. Request an app upgrade for more; exhaustion returns HTTP `429`.

### MyDHL Express

- An active DHL Express customer account is required.
- Send issued credentials with pre-emptive HTTP Basic authentication.
- Test at `https://express.api.dhl.com/mydhlapi/test`; use `https://express.api.dhl.com/mydhlapi` in production.
- Test credentials allow 500 service invocations per day.

### Parcel Germany

- Sandbox: `https://api-sandbox.dhl.com/parcel/de/shipping/v2/`.
- Production: `https://api-eu.dhl.com/parcel/de/shipping/v2/`; explicit approval follows successful sandbox use.
- A newly created API key may not work until 00:00 CEST.
- Use a non-interactive system user in production. Its portal password expires after 365 days; a personal user's expires after 90 days.

## Compatibility and failure handling

### eCommerce Americas evolution

Within an existing API version, treat these as backward-compatible changes:

- new optional request or query fields;
- extra response fields;
- property reordering;
- new methods;
- new resources.

Clients must tolerate those changes. Use product codes, error codes, and event IDs as integration keys instead of mutable names or descriptions.

Error responses link to `https://api.dhlecs.com/docs/errors/<error-code>`. Two independent controls can return `429` with distinct details:

- Spike Arrest limits parallel requests to a resource.
- Quota Violation limits account-specific weekly volume across resources.

Provide queue-and-retry handling for either case.

### Parcel Germany batch semantics

- `POST /orders` validates or creates shipments; `GET /orders` retrieves documents; `DELETE /orders` cancels shipments.
- `POST /manifests` closes out shipments; `GET /manifests` retrieves manifests.
- `GET /labels` follows the label URL returned by `POST /orders`.
- `GET /` checks the version but does not disclose patch-level updates.
- Array responses retain request order, and a one-entry request still returns a one-entry array.
- Use `validate=true` to check fields and business rules without creating a shipment.

## High-value shipment rules

### eCommerce Americas

- International label requests can include `additionalPartyAddress` and `customsDetails.itemReferences`; use published Item Reference Type Codes for item reference values.
- Domestic Label requests accept the `customsDetails` array only for APO, FPO, DPO, and non-continental US destinations. Omit it elsewhere.
- Manifest requests accept optional `products` to limit or group closeout by product.
- Put optional `deliveryInstructions` in `consigneeAddress`.
- Preserve `postalCode` and `country` from each Tracking `events` object when processing event location.

### MyDHL Express

- Use `Product` for lightweight one-piece capability lookup. `Rating` adds account rates, value-added services, and estimated delivery.
- DHL recommends rating before shipment creation so submitted products and services are eligible.
- JSON must not begin with a byte-order mark.
- For standardized packaging, a package type code lets Rating and Shipment omit dimensions because the code supplies them.
- `addPiece` works only before DHL pickup or a recorded scan.
- Declarable non-document shipments require `exportDeclaration`; non-declarable shipments may omit currency code and incoterm.
- Shipment data can be validated without creating a label.
- Monetary, weight, duty, tax, and additional-charge values must be positive.

### Parcel Germany

- Each physical parcel is one shipment; multipackage shipments are unsupported. `costCenter` values such as `1/2` and `2/2` can visually relate separate labels.
- Weight is mandatory in grams or kilograms.
- Dimensions are optional, but unit, length, width, and height must be supplied together.
- Omit missing consignee phone or email, or send `null`; do not send whitespace.
- Warnings do not invalidate an accompanying label. Set `mustEncode=true` when creation must require an encodable address.
- Shipments remain editable only until manifesting. Before then, cancel with `DELETE /orders` and recreate with `POST /orders`; manifested shipments cannot be changed.
- International parcels must be manifested before physical handoff.

## High-value location rules

- `/find-by-address` requires at least three total characters across `addressLocality`, `postalCode`, and `streetAddress` and first resolves the address to coordinates.
- The default radius is 5,000 metres and the maximum is 1,000,000 metres.
- Repeating `serviceType` creates an AND condition.
- `parcel:pick-up-all` and `parcel:drop-off-all` are query-only family matchers and are not returned as service values.
- Use `providerType=parcel` to exclude Express locations from Post & Parcel results.
- A valid but uncovered country code can return `200` with no locations; an invalid code returns `400`.
- Direct shipment addressing is not for DHL Express and requires a designated Postfiliale number exposed as `keywordId`. Supply the recipient email for pickup notification.
- Location Data must not be stored or modified. When used with other logistics providers' location data, show all DHL locations returned for the address and do not select or recommend individual DHL locations contrary to DHL's interests.

## Product and dangerous-goods checks

- eCommerce Americas product code `PLX` is DHL Parcel International Expedited. Apply its regulations and content-category rules; PLX does not support dangerous goods.
- Paperless Trade dangerous-goods content categories `01`–`06` and `40` are restricted to Canada and Mexico, not Canada alone. Reject other destinations.
- Parcel Germany validates request `product` against the billing-number procedure. Available services also depend on product, user permissions, and mutually exclusive combinations.
- DHL Kleinpaket replaced Warenpost on January 1, 2025. `Consignee.ContactAddress.country` is mandatory for Kleinpaket as an ISO 3166-1 alpha-3 code.
- A requested Parcel Germany `premium=false` can still become Premium where the destination lacks an Economy product; most EU countries behave this way, while Switzerland offers both.

## Consult the detailed references

Use the linked references for complete field lists, service identifiers, country coverage, label formats, customs codes, image types, address layouts, response mappings, and lifecycle limits. Preserve the documented division-specific scope and conditions when transferring any item into implementation code.
