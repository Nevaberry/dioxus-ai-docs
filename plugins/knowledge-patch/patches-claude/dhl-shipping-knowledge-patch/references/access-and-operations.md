# Access and operations

## eCommerce Americas v4

### Scope and origin

Version 4 covers product discovery, duty and tax calculation, labels,
manifests, tracking, and returns for domestic and international packages. It
supports the eCommerce Americas product portfolio only when the package
originates in the United States or Canada.

### Compatibility and integration keys

Within an existing API version, treat the following as backward-compatible:

- new optional request or query fields;
- additional response fields;
- property reordering;
- new methods; and
- new resources.

Clients must tolerate those changes. Use product codes, error codes, and event
IDs as integration keys rather than mutable names or descriptions.

### Environments and production verification

Use `https://api-sandbox.dhlecs.com` for testing and
`https://api.dhlecs.com` for production. Labels and manifests do not cross
environments. Pickup access, products, capacity, account master data,
distribution centers, and allowed content categories can also differ. Verify
the production setup independently before launch.

### Errors, throttling, network, and TLS

Error responses link to
`https://api.dhlecs.com/docs/errors/<error-code>`. Two independent rate limits
can return `429`, with distinct error details:

- Spike Arrest limits parallel requests to a resource.
- Quota Violation limits account-specific weekly volume across resources.

Integrations need queue-and-retry handling for both. The References published
new inbound and outbound IP addresses for sandbox and production effective
August 18, 2026, together with supported TLS cipher versions. Network
allowlists and TLS policy should be checked against those reference values
before connecting.

## Location Finder v1

### Endpoint, access, and quota

The production API is GET-only at
`https://api.dhl.com/location-finder/v1`. Every call requires an approved
app's key in the `DHL-API-Key` header.

```bash
curl --get 'https://api.dhl.com/location-finder/v1/find-by-address' \
  -H 'DHL-API-Key: ApiKeyPasteHere' \
  --data-urlencode 'countryCode=GB' \
  --data-urlencode 'addressLocality=London'
```

New access starts at 500 calls per day. Higher limits require an app upgrade
request, and exhausted limits return HTTP `429`.

### Provider coverage and country errors

Post & Parcel and eCommerce coverage includes `AT`, `BE`, `BG`, `CY`, `CZ`,
`DE`, `DK`, `EE`, `ES`, `FI`, `FR`, `GB`, `GR`, `HR`, `HU`, `IT`, `LT`, `LU`,
`LV`, `NL`, `NO`, `PL`, `PT`, `RO`, `SE`, `SI`, and `SK`. Express has a
separate, much broader country set.

A syntactically valid but uncovered country code can return `200` with no
locations. An invalid country code returns `400`.

### Location Data terms

The Location Data terms allow publishing, display, or other use only in
connection with other logistics or transportation providers' location data.
When doing so, show all DHL locations returned for the address; do not select
or recommend individual locations contrary to DHL's interests.

Do not store or modify Location Data. Competitive analysis or derivation
requires prior written consent.

## MyDHL API

### Account, authentication, and environments

MyDHL API requires an active DHL Express customer account. Use pre-emptive
HTTP Basic authentication with issued credentials. Test requests use
`https://express.api.dhl.com/mydhlapi/test`, and production requests use
`https://express.api.dhl.com/mydhlapi`. Test credentials are limited to 500
service invocations per day.

### Product selection and validation

`Product` is the lightweight one-piece capability lookup. `Rating` adds
account rates, value-added services, and estimated delivery. DHL recommends
rating before shipment creation so that only eligible products and services
are submitted.

Requests first undergo schema/cardinality validation and then business-rule
validation. Findings are returned in the operation's result message. JSON
must not begin with a byte-order mark.

### Quote and data-use constraints

Rates and transit promises are indicative and can differ from the tendered
shipment. They may omit duties, taxes, customs charges, surcharges, or fees.
Product and Rating data must not be stored, modified, or disclosed to third
parties without prior written consent.

Landed Cost requires an item catalogue containing customs data such as HS
codes, plus supplied values such as freight and insurance.

## Parcel Germany Shipping v2

### Scope and merchant eligibility

Shipping v2 creates and manages labels and export documents for goods
shipments originating in Germany, domestically or to another country. It
cannot create documents for shipments originating abroad.

It is designed for Post & Parcel Germany business customers with a contract,
a Business Customer Portal account, and typically more than 200 shipments per
year. Lower-volume senders without an EKP use the private-customer shipping
API.

### Billing numbers and service eligibility

The 14-character `billingNumber` has no separators and consists of:

1. the ten-digit EKP;
2. the two-character procedure/product; and
3. a numeric or alphabetic participation, `00`–`99` or `AA`–`ZZ`.

```text
1234567890 + 53 + 01 = 12345678905301
```

Integrations must allow multiple billing numbers or participations. Merchants
can use them to separate locations, seasons, terms, or services such as
GoGreen. The request's `product` is validated against the procedure; service
availability also depends on the product, user permissions, and mutually
exclusive combinations.

### OAuth 2, credentials, and rotation

Obtain an OAuth 2 access token from the separately assigned Post & Parcel
Germany Authentication API by sending the Business Customer Portal username
and password with the app API key and secret. Use the token as
`Authorization: Bearer ...`.

```bash
curl -X POST https://api-sandbox.dhl.com/parcel/de/account/auth/ropc/v1/token \
  -d 'grant_type=password' -d 'username=...' -d 'password=...' \
  -d 'client_id=...' -d 'client_secret=...'
```

Basic Auth plus the `dhl-api-key` header remains a v2 alternative, but it is
slated for removal in a future major version. A production integration should
use a non-interactive system user. Its portal password expires after 365 days,
compared with 90 days for a personal user. A newly created API key may not
become usable until 00:00 CEST.

### Environments, access, and retired transports

Use `https://api-sandbox.dhl.com/parcel/de/shipping/v2/` for integration
testing and `https://api-eu.dhl.com/parcel/de/shipping/v2/` for production.
Production access requires explicit approval after successful sandbox use.

REST v2 is active. GKV SOAP 1.x and 2.x are retired, and GKV SOAP 3.x reached
its stated sunset on May 31, 2026.

### Resources, arrays, and validation

- `GET /` checks the version.
- `POST /orders` validates or creates shipments.
- `GET /orders` retrieves documents.
- `DELETE /orders` cancels shipments.
- `POST /manifests` closes out shipments, and `GET /manifests` retrieves
  manifests.
- `GET /labels` follows the label URL returned by `POST /orders`.

For an array request, response entries preserve request order. A one-entry
request still returns a one-entry array. Use `validate=true` to check fields
and business rules without creating the shipment.

### Schema and version-check migration

The version check does not disclose patch-level updates. `officeOfOrigin` is
deprecated. Follow the corrected `GET /labels`, `GET /manifests`,
`shippingConditions`, and `product` schemas.
