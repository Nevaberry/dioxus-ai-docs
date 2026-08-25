---
name: posti-matkahuolto-knowledge-patch
description: Posti / Matkahuolto
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Posti / Matkahuolto Merchant Shipping

Load this skill when implementing, reviewing, or troubleshooting merchant
shipping integrations that use the Posti or Matkahuolto interfaces documented
here. It distinguishes the providers' API families, credentials, environments,
request formats, and response contracts.

## Reference index

| Reference | Topics |
| --- | --- |
| [Matkahuolto pickup points](references/matkahuolto-pickup-points.md) | API access, pickup-point search, filters, replies, datasets, and production transition |
| [Matkahuolto shipments](references/matkahuolto-shipments.md) | XML label requests, shipment fields, products, labels, parcels, customs, dangerous goods, EDI, replies, and errors |
| [Matkahuolto tracking](references/matkahuolto-tracking.md) | Tracking queries, formats, event codes, conditional fields, and errors |
| [Posti merchant operations](references/posti-merchant-operations.md) | Versioned gateway, OAuth profiles, pickup points, delivery estimates, labelless sending, and API errors |
| [Posti Tracking API v7](references/posti-tracking-v7.md) | Authentication, lookup aliases, generic search, filters, pagination, responses, events, quantities, reservations, and generator caveats |

## Critical compatibility rules

### Do not mix Posti credential profiles

The Posti versioned gateway exchanges `client_id` and `client_secret` as form
fields at `https://gateway-auth.posti.fi/api/v1/token`.

The separate service-account flow requires a Posti contract and an account
obtained through customer service. It sends `accountname:secret` with HTTP
Basic authentication to `https://oauth2.posti.com/oauth/token`; QA and UAT use
`oauth2.barium.posti.com`.

All operations at the `https://gateway.posti.fi/2026-04` base URL require a
bearer token. The Posti Tracking REST API separately uses
`https://api.posti.fi/tracking/7` and inherits an OAuth 2.0 client-credentials
scheme whose token URL is `/tracking/oauth/token`.

### Remove obsolete Matkahuolto shipment fields

For Matkahuolto shipment request version 2.24, do not send COD fields,
shipment/root-level ADR codes, or special-handover fields. Put dangerous-goods
data at parcel level in `DangerousGoodsRow`.

`E01` is the old ADR special-handling code and should be replaced by `VA` or
`LQ`. The version history assigns `SD` to same-day delivery even though the
current code table omits it.

### Respect strict and incomplete schemas

Posti versioned-gateway request objects declare `additionalProperties: false`;
omit undeclared JSON fields.

Posti Tracking API v7 declares no required properties in any of its 48
component schemas, so consumers must tolerate absent response fields.

The Tracking API v7 specification places typed success payloads under
`default`, not an explicit 2xx response. Status-driven client generators may
need an override for `SearchResponseDto` or `ReservationStatusesResponseDto`.

### Correct Tracking API v7 generated parameters when needed

The generic `keys` schema encodes the entire choice list as one enum string,
and the path form contains malformed `!delivery_groupsequence`. Generated
clients may need this parameter corrected to follow the prose contract.

Array schemas for reservation filters do not define custom serialization,
while their examples use comma-separated strings. Verify serialization when
bypassing a generated client.

### Treat the v7 pagination limits as a documented caveat

Tracking API v7 declares `limit` as 1–1000 with a default of `100`, while the
operation text separately warns of a hard 100-shipment return limit. Follow
returned counts and test paging semantics rather than treating the schema
maximum as the page size.

`combined=true` is typed as a string and is explicitly warned not to work
reliably with pagination.

## Matkahuolto quick reference

### Access and environments

- A valid agreement is required for the open APIs.
- Free API credentials are required for testing and implementation.
- Existing customers request missing credentials and customer IDs through the
  designated form, not technical-support email.
- The test environment returns correctly formatted responses but does not
  process submitted consignments.
- Moving the integration to production only requires changing the contact
  address.

### Pickup-point search

POST `MHSearchOfficesRequest` to
`https://extservices.matkahuolto.fi/noutopistehaku/public/v2/searchoffices`
with `Content-Type: application/xml` or `text/xml`.

`Login` is the registered customer number. Address search needs `PostalCode`
or `City`; `Id` directly looks up a known office. The principal defaults are
`Country=FI`, `ResponseType=XML`, `MaxResults=5`, and `Coordinates=N`.

Pickup points may instead be periodically downloaded into the store's own
database, such as once daily.

### Shipment creation

Send `MHShipmentRequest` XML with `Content-Type: text/xml` to
`https://extservices.matkahuolto.fi/mpaketti/mhshipmentxml`; use the
`extservicestest` host for testing.

`UserId` is the supplied account number without leading zeroes. One request
may contain multiple `Shipment` elements, with all labels returned in one PDF.
An empty `ShipmentNumber` is allocated by the service.

Dates use `DD.MM.YYYY`, counts are integers, and decimals require a dot.

### Tracking

GET `https://extservices.matkahuolto.fi/mpaketti/public/tracking` with HTTP
Basic authentication. Supply either `ids` or a `from`/`to` time range; `ids`
is a comma-separated list of at most ten shipment or parcel IDs.

XML is the default response. Send `Accept: application/json` for JSON. A valid
query without matching events returns an empty message rather than an error.

Matkahuolto tracking data may be displayed directly in an online store in
addition to the recipient-facing Track & Trace service.

## Posti merchant quick reference

### Versioned gateway

The specification identifies API version `2026-04.0`, served from
`https://gateway.posti.fi/2026-04`, with LTS support promised through
2029-04-30.

### Pickup points

POST `/pickuppoints` with required `searchCriteria`. Searches support
street/postcode location, coordinate and radius, rectangle, free text, and
parcel-locker modes.

`Accept-Language` defaults to `fi` and accepts `fi`, `sv`, `da`, `en`, `et`,
`lv`, or `lt`. `X-Posti-LogisticsId` is optional.

Use GET `/pickuppoints/{id}` or
`/pickuppoints/{countryCode}/{pupCode}` for targeted lookup. GET
`/pickuppoints/{countryCode}` lists points and returns a reusable
`pagingContinuationToken`.

### Estimates and labelless sending

POST `/estimate` with required time, origin, destination, and product inside
an `estimate` object. Delivery estimates can also be requested as a pickup
point search extension.

POST `/labelless` with a tracking number to obtain a sending code. GET
`/labelless/{trackingNumber}` performs the same lookup, and GET
`/labelless/shipment/{sendingCode}` resolves a sending code back to shipment
data.

## Posti Tracking API v7 quick reference

### Lookup paths and generic search

All shipment searches return the same response envelope. Dedicated paths map
lookup values to parcel or freight keys, and do not all search both families.
In particular, `consignmentnumber` and `errandcode` are parcel-only, while
`goodsitemid/{goodsItemId}` is documented as an alias for
`freight_tracking_number`.

Use GET `/tracking/7/shipments/find` with a required `keywords` array of 1–100
unique strings, or `/tracking/7/shipments/find/{keyword}` for one value of
3–60 characters. `keys` defaults to `all` and supports comma-separated groups
or keys with `!` negation.

### Common filters and response envelope

Shipment searches support `lastModified`, `type=ANY|FREIGHT|PARCEL`,
`order=ASC|DESC`, response-unit selectors, `combined`, `start`, and `limit`.

`SearchResponseDto` has independent `freightShipments` and `parcelShipments`
arrays. Parcel and freight results expose distinct fields and status codes.

### Restricted operations

Restricted GET `/tracking/7/shipments/event/date` searches for shipments with
events in a date-time interval; `from` is inclusive and `to` is exclusive.

Restricted GET `/tracking/7/reservations/status` requires a delivery-window
`from` and `to`, destination `country`, and a `postcode` array. Its response
contains reservation windows, counts, and tracking numbers.
