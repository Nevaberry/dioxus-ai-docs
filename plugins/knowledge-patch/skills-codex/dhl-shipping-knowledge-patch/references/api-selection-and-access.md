# API Selection and Access

## eCommerce Americas

### Scope and origin

Version 4 covers product discovery, duty and tax calculation, labels, manifests, tracking, and returns for domestic and international packages. It supports the full eCommerce Americas product portfolio only when packages originate in the United States or Canada.

### Compatible evolution and identifiers

Within an existing API version, new optional request or query fields, extra response fields, property reordering, new methods, and new resources are backward-compatible. Clients must tolerate these changes and use product codes, error codes, and event IDs instead of mutable names or descriptions as integration keys.

### Environments

Use `https://api-sandbox.dhlecs.com` for testing and `https://api.dhlecs.com` for production. Labels and manifests do not cross environments. Pickup access, products, capacity, account master data, distribution centers, and allowed content categories can differ, so verify production setup separately before launch.

### Errors and throttling

Error responses link to `https://api.dhlecs.com/docs/errors/<error-code>`. Rate limiting has two independent controls:

- Spike Arrest constrains parallel requests to a resource.
- Quota Violation constrains account-specific weekly volume across resources.

Both return `429` with distinct error details. Integrations need queue-and-retry handling for either.

### Network allowlists and TLS

The References published new inbound and outbound IP addresses for sandbox and production effective August 18, 2026, together with supported TLS cipher versions. Check network allowlists and TLS policy against those reference values before connecting.

## DHL Location Finder

### Access and quota

The production API is GET-only at `https://api.dhl.com/location-finder/v1`. Every call requires an approved app's key in `DHL-API-Key`. New access starts at 500 calls per day; higher limits require an app upgrade request, and an exhausted limit returns HTTP `429`.

```bash
curl --get 'https://api.dhl.com/location-finder/v1/find-by-address' \
  -H 'DHL-API-Key: ApiKeyPasteHere' \
  --data-urlencode 'countryCode=GB' \
  --data-urlencode 'addressLocality=London'
```

### Search entry points and bounds

Search by address, coordinates, location ID, or `keywordId`. `/find-by-address` first resolves the address to coordinates and requires at least three characters in total across `addressLocality`, `postalCode`, and `streetAddress`. The default radius is 5,000 metres and the maximum is 1,000,000 metres. `/find-by-geo` accepts optional `countryCode` to filter results.

### Provider coverage and country errors

Post & Parcel and eCommerce coverage includes `AT`, `BE`, `BG`, `CY`, `CZ`, `DE`, `DK`, `EE`, `ES`, `FI`, `FR`, `GB`, `GR`, `HR`, `HU`, `IT`, `LT`, `LU`, `LV`, `NL`, `NO`, `PL`, `PT`, `RO`, `SE`, `SI`, and `SK`. Express has its own, much broader country set.

A syntactically valid but uncovered country code can return `200` with no locations. An invalid country code returns `400`.

### Location Data terms

Location Data may be published, displayed, or otherwise used only in connection with other logistics or transportation providers' location data. In that use, show all DHL locations returned for the address without selecting or recommending individual locations contrary to DHL's interests. Do not store or modify Location Data. Competitive analysis or derivation requires prior written consent.

## MyDHL Express

### Account, authentication, and environments

MyDHL API requires an active DHL Express customer account. Use pre-emptive HTTP Basic authentication with issued credentials. Test at `https://express.api.dhl.com/mydhlapi/test` and use `https://express.api.dhl.com/mydhlapi` for production. Test credentials are limited to 500 service invocations per day.

### Product selection and validation

`Product` is a lightweight one-piece capability lookup. `Rating` adds account rates, value-added services, and estimated delivery. DHL recommends rating before creating a shipment so only eligible products and services are submitted.

Requests first undergo schema and cardinality validation, then business-rule validation. Findings appear in the operation's result message. JSON must not start with a byte-order mark.

### Reference Data and service points

The MyDHL Reference Data resource supplies DHL Express reference datasets so enum lists need not be hard-coded. Its Service Point operation finds Express pickup and drop-off points from a postal address, service-point ID, or geocode. This contract is specific to MyDHL and must not be substituted for another DHL division's location API.

## Parcel Germany Shipping v2

### Scope and merchant eligibility

Shipping v2 creates and manages labels and export documents for goods shipments originating in Germany, either domestically or to another country. It cannot create documents for shipments originating abroad.

It is intended for Post & Parcel Germany business customers with a contract, a Business Customer Portal account, and typically more than 200 shipments per year. Lower-volume senders without an EKP use the private-customer shipping API.

### Billing numbers

The 14-character `billingNumber` consists of the ten-digit EKP, the two-character procedure or product, and a numeric or alphabetic participation (`00`–`99` or `AA`–`ZZ`), without separators.

```text
1234567890 + 53 + 01 = 12345678905301
```

Allow multiple billing numbers or participations because merchants can separate locations, seasons, terms, or services such as GoGreen. The request `product` is validated against the procedure. Available services also depend on the product, user permissions, and mutually exclusive combinations.

### OAuth and credential rotation

OAuth 2 obtains an access token from the separately assigned Post & Parcel Germany Authentication API. Send the Business Customer Portal username and password plus the app API key and secret, then use the token as `Authorization: Bearer ...`.

```bash
curl -X POST https://api-sandbox.dhl.com/parcel/de/account/auth/ropc/v1/token \
  -d 'grant_type=password' -d 'username=...' -d 'password=...' \
  -d 'client_id=...' -d 'client_secret=...'
```

Basic Auth with the `dhl-api-key` header remains a v2 alternative but is slated for removal in a future major version. Production integrations should use a non-interactive system user: its portal password expires after 365 days, compared with 90 days for a personal user. A newly created API key may not become usable until 00:00 CEST.

### Environments and retirement

Use `https://api-sandbox.dhl.com/parcel/de/shipping/v2/` for integration testing and `https://api-eu.dhl.com/parcel/de/shipping/v2/` for production. Production access requires explicit approval after successful sandbox use.

REST v2 is active. GKV SOAP 1.x and 2.x are retired, and GKV SOAP 3.x reached its stated sunset on May 31, 2026.

### Resources and array responses

- `GET /` checks the version.
- `POST /orders` validates or creates shipments.
- `GET /orders` retrieves documents.
- `DELETE /orders` cancels shipments.
- `POST /manifests` closes out shipments.
- `GET /manifests` retrieves manifests.
- `GET /labels` follows the label URL returned by `POST /orders`.

For an array request, response entries retain request order. Even a one-entry request returns a one-entry array. Use `validate=true` to check fields and business rules without creating a shipment.
