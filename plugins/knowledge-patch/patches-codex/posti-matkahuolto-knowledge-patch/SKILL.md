---
name: posti-matkahuolto-knowledge-patch
description: Posti / Matkahuolto
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Posti / Matkahuolto merchant shipping

Load this skill when implementing or reviewing Posti or Matkahuolto merchant
shipping integrations, including pickup-point discovery, shipment creation,
labels, delivery estimates, labelless sending, tracking, or authentication.

Keep the two providers and their API families distinct. In particular, Posti's
versioned merchant gateway, Posti's separate service-account OAuth flow, Posti
Tracking API v7, and Matkahuolto's XML interfaces use different hosts,
credentials, payloads, and response conventions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Interface Hub and access](references/interface-hub-and-access.md) | Matkahuolto agreements, credentials, XML labels, EDI, test behavior, pickup-point data, and embedded tracking |
| [Matkahuolto pickup points](references/matkahuolto-pickup-points.md) | Office-search endpoint, request defaults, filters, reply fields, CSV behavior, and errors |
| [Matkahuolto shipments and tracking](references/matkahuolto-shipments-and-tracking.md) | Shipment XML, routing, products, labels, customs, dangerous goods, replies, errors, and tracking |
| [Posti merchant services](references/posti-merchant-services.md) | Gateway authentication, pickup points, delivery estimates, labelless sending, and API errors |
| [Posti Tracking API v7](references/posti-tracking-v7.md) | Authentication, lookup aliases, generic search, paging, response schemas, events, and reservations |

## Critical compatibility rules

### Keep Posti credential profiles separate

For the versioned Posti gateway, exchange `client_id` and `client_secret` as
form fields at `https://gateway-auth.posti.fi/api/v1/token`, then send the
bearer token on all operations.

The separate Posti service-account flow requires a Posti contract and an
account obtained through customer service. It uses HTTP Basic authentication
with `accountname:secret` at `https://oauth2.posti.com/oauth/token`; QA and UAT
use `oauth2.barium.posti.com`.

Service-account tokens expire after one hour by default. Five invalid logins
lock the account for one hour. Installations using `oauth.posti.com` or
`oauth.posti.fi` must account for the replaced TLS certificate;
`oauth2.posti.com` needs no certificate-related change.

### Do not send fields removed from Matkahuolto shipment XML 2.24

Do not send COD fields, shipment- or root-level ADR codes, or special-handover
fields. Place dangerous-goods data at parcel level in `DangerousGoodsRow`.

Replace the old `E01` ADR special-handling code with `VA` or `LQ`.

### Account for Posti Tracking API schema defects

The generic `keys` parameter's OpenAPI schema encodes its entire choice list as
one enum string, and the path form contains malformed
`!delivery_groupsequence`. Generated clients may need this parameter corrected
to follow the prose contract.

The tracking specification declares error statuses without bodies and places
the typed success payload under `default`, rather than an explicit 2xx status.
Status-based client generators may need an override for `SearchResponseDto` or
`ReservationStatusesResponseDto`.

None of the 48 component schemas declares required properties. Consumers must
tolerate absent fields.

### Treat tracking pagination conservatively

Posti Tracking API v7 declares `limit` as 1–1000 with a default of `100`, while
the operation text separately warns of a hard 100-shipment return limit.
Follow returned counts and test paging semantics. `combined=true` is typed as a
string and is explicitly warned not to work reliably with pagination.

## Matkahuolto quick reference

### Choose the integration surface

- Submit XML label requests with HTTP POST over HTTPS; unencrypted HTTP is
  rejected. A successful XML response contains the reply and an address-label
  PDF.
- Integrate pickup points through the real-time API or periodically download
  the dataset into the store's database, such as once daily.
- Send shipment information by API or file transfer. EDI messages may be XML
  or CSV.
- Display Matkahuolto tracking data directly in the store, in addition to the
  recipient-facing Track & Trace service.

The test environment returns correctly formatted responses but does not
process consignments. Production activation only requires changing the contact
address.

### Search pickup points

POST `MHSearchOfficesRequest` to:

```text
https://extservices.matkahuolto.fi/noutopistehaku/public/v2/searchoffices
```

Use `Content-Type: application/xml` or `text/xml`. `Login` is the registered
customer number. Address search requires `PostalCode` or `City`; use `Id` to
look up one known office.

Defaults are `Country=FI`, `ResponseType=XML`, `MaxResults=5`, and
`Coordinates=N`. The legacy `/noutopistehaku/public/searchoffices` address runs
the same search but URL-encodes the response.

### Submit shipments

Send `MHShipmentRequest` XML with `Content-Type: text/xml` to:

```text
https://extservices.matkahuolto.fi/mpaketti/mhshipmentxml
```

Use the `extservicestest` host for testing. `UserId` is the supplied account
number without leading zeroes. A request may contain multiple `Shipment`
elements, and their labels are returned in one PDF.

The mandatory shipment fields are shipment/message type, weight, package
count, sender account, receiver name/postal code/city, and product code. Empty
`ShipmentNumber` asks the service to allocate one. Dates use `DD.MM.YYYY`,
counts are integers, and decimal values use a dot.

Always represent the payer account with `SenderId`, `ReceiverId`, or `PayerId`.
`PayerCode` is `S`, `R`, or `O`; `O` makes `PayerId` mandatory.

### Query tracking

GET `https://extservices.matkahuolto.fi/mpaketti/public/tracking` with HTTP Basic
authentication. Supply either `ids`, a comma-separated list of at most ten
shipment or parcel IDs, or `from`/`to` date-time input. XML is the default;
`Accept: application/json` selects JSON.

A valid query with no matching events returns an empty message rather than an
error.

## Posti merchant quick reference

### Authenticate to the versioned gateway

The merchant specification identifies API version `2026-04.0`, with production
base URL `https://gateway.posti.fi/2026-04` and LTS support through 2029-04-30.
Every operation requires a bearer token.

```http
POST /api/v1/token HTTP/1.1
Host: gateway-auth.posti.fi
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
```

### Search and retrieve pickup points

POST `/pickuppoints` with required `searchCriteria`. Supported searches are
street/postcode location, coordinate and radius, rectangle, free text, and
parcel locker. `Accept-Language` defaults to `fi` and accepts `fi`, `sv`, `da`,
`en`, `et`, `lv`, or `lt`; `X-Posti-LogisticsId` is optional.

Use GET `/pickuppoints/{id}` or
`/pickuppoints/{countryCode}/{pupCode}` for targeted lookup. GET
`/pickuppoints/{countryCode}` lists points and returns a reusable
`pagingContinuationToken`.

### Request estimates and labelless codes

POST `/estimate` with required `time`, origin, destination, and product inside
an `estimate` object. The response is an `estimates` array whose delivery
`time` may be null.

POST `/labelless` with a tracking number to obtain a sending code;
`validation.noEdiCheck` is optional and defaults to `false`. GET
`/labelless/{trackingNumber}` performs the same lookup, and GET
`/labelless/shipment/{sendingCode}` resolves the code back to shipment data.

Request objects declare `additionalProperties: false`; omit undeclared JSON
fields. Error objects always require `errorCode`, `message`, and `details`, even
when `details` is null.

## Posti Tracking API v7 quick reference

Use base URL `https://api.posti.fi/tracking/7`. Every operation inherits an
OAuth 2.0 client-credentials scheme with token URL `/tracking/oauth/token`.
Send the bearer token and request either ordinary JSON or
`application/vnd.tracking.api.v1+json`.

Use dedicated identifier paths when appropriate, or GET
`/tracking/7/shipments/find` with a required `keywords` array of 1–100 unique
strings. GET `/tracking/7/shipments/find/{keyword}` accepts one value of 3–60
characters.

All shipment searches support `lastModified`, `type=ANY|FREIGHT|PARCEL`,
`order=ASC|DESC`, response-unit selectors, `start`, and `limit`. Restricted GET
`/tracking/7/shipments/event/date` searches events in an interval where `from`
is inclusive and `to` is exclusive.

`SearchResponseDto` has independent `freightShipments` and `parcelShipments`
arrays. Quantity query selectors use long unit names, while response objects
use abbreviated units.

Restricted GET `/tracking/7/reservations/status` requires delivery-window
`from`/`to`, destination `country`, and a `postcode` array. Array examples are
comma-separated strings even though the schemas do not declare custom
serialization; verify serialization when bypassing a generated client.

## Review checklist

- Verify the provider, API family, base host, credential profile, and content
  type before comparing request fields.
- For Matkahuolto, keep pickup-point defaults, shipment XML conventions, and
  tracking response selection explicit.
- For Posti merchant APIs, reject undeclared JSON properties and preserve
  required error fields even when `details` is null.
- For Posti Tracking API v7, tolerate absent response fields and review
  generated handling of `keys`, success responses, array serialization, and
  pagination.
- Consult the topic references for complete field values, nested limits,
  statuses, event codes, and error-code mappings.
