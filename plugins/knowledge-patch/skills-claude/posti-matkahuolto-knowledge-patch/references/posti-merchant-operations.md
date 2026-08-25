# Posti Merchant Operations

## Versioned gateway and support lifetime

The specification identifies API version `2026-04.0`. Its production base URL
is:

```text
https://gateway.posti.fi/2026-04
```

Posti promises LTS support through 2029-04-30. All operations in this version
require a bearer token.

## Versioned-gateway OAuth profile

Exchange `client_id` and `client_secret` as form fields at
`https://gateway-auth.posti.fi/api/v1/token`:

```http
POST /api/v1/token HTTP/1.1
Host: gateway-auth.posti.fi
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
```

## Service-account OAuth profile

The separate Posti service-account flow requires both a Posti contract and an
account obtained through customer service. Send `accountname:secret` with HTTP
Basic authentication to `https://oauth2.posti.com/oauth/token`. QA and UAT use
`oauth2.barium.posti.com`; production uses `oauth2.posti.com`.

```http
POST /oauth/token?grant_type=client_credentials HTTP/1.1
Host: oauth2.posti.com
Accept: application/json
Authorization: Basic BASE64_ACCOUNTNAME_COLON_SECRET
```

Service-account tokens expire after one hour by default. Five invalid logins
lock the account for one hour.

Installations still using `oauth.posti.com` or `oauth.posti.fi` must account
for their replaced TLS certificate. `oauth2.posti.com` needs no
certificate-related change.

## Pickup-point search modes

POST `/pickuppoints` with required `searchCriteria`. It supports:

- street and postcode location;
- coordinate and radius;
- rectangle;
- free text;
- parcel-locker search.

`Accept-Language` defaults to `fi` and accepts `fi`, `sv`, `da`, `en`, `et`,
`lv`, or `lt`. `X-Posti-LogisticsId` is an optional header.

```json
{
  "searchCriteria": {
    "location": {
      "coordinates": { "latitude": 60.168954, "longitude": 24.934123 },
      "radius": { "unit": "m", "value": 450 }
    },
    "parcelLocker": true,
    "serviceFilters": {
      "outdoorLocker": false,
      "product": { "code": "2103" },
      "lockerReservable": true
    }
  },
  "limit": 15
}
```

Other service filters are `wheelchairAccessibility`, `openOnWeekends`,
`ADRLimitedQuantities`, and `saturdayDelivery`.

A rectangular search uses `searchCriteria.rectangle` with all four of
`swLatitude`, `swLongitude`, `neLatitude`, and `neLongitude`.

## Pickup-point search extensions

Searches can request a delivery estimate and average locker occupancy in
`extensions`. The estimate requires:

- `time`;
- origin `postcode` and `countryCode`;
- `product.code`.

The origin may also carry `pickuppointId` or `gln`. The product may carry
`additionalServicesCodes`.

```json
{
  "searchCriteria": {
    "location": { "postcode": "00100", "countryCode": "FI" }
  },
  "extensions": {
    "estimate": {
      "time": "2025-09-02T16:30:00Z",
      "origin": { "postcode": "01530", "countryCode": "FI" },
      "product": { "code": "2103" }
    },
    "averageLockerOccupancyRate": true
  }
}
```

Matching response extensions contain `estimate.time` and locker-occupancy
`averageRate` plus `description`.

## Pickup-point retrieval and pagination

Use these targeted lookup operations:

- GET `/pickuppoints/{id}`;
- GET `/pickuppoints/{countryCode}/{pupCode}`.

GET `/pickuppoints/{countryCode}` lists points and returns a reusable
`pagingContinuationToken`.

Despite its name, the `{countryCode}` path value accepts either a two- or
three-letter country code, or that code followed by a digit-led alphanumeric
pickup-point ID prefix. It matches:

```regex
^[a-zA-Z]{2,3}([0-9][0-9a-zA-Z]*)?$
```

These GET operations accept the same `Accept-Language` and optional
`X-Posti-LogisticsId` headers as search.

## Pickup-point response fields

Responses wrap results in `pickupPoints`. Each point requires:

- `id`;
- `publicName`;
- `careOf`;
- `parcelLocker`;
- availability;
- location;
- capabilities.

Optional fields include `routingServiceCode`, `distanceInMeters`, extensions,
`pupCode`, and `externalId`.

Availability contains regular opening hours and exceptions. Location includes
country, street, postcode, city, municipality, coordinates, and optional
`specificLocation` and `routingPostcode`.

## Standalone delivery estimates

POST `/estimate` with an `estimate` object containing required date-time
`time`, origin, destination, and product. Origin and destination each require
`countryCode` and may identify a `postcode`, `pupCode`, or `gln`. Product
requires `code` and may include `additionalServicesCodes`.

```json
{
  "estimate": {
    "time": "2025-09-02T16:30:00Z",
    "origin": { "postcode": "01530", "countryCode": "FI" },
    "destination": { "pupCode": "001003200", "countryCode": "FI" },
    "product": { "code": "2103" }
  }
}
```

Optional context is:

- `logisticsPhase`, with `event` and `reason` together;
- `shipmentSeq`;
- `senderAgreement`;
- `payerAgreement`;
- `shipmentType`;
- `partyName`.

The response is an `estimates` array whose entries contain a possibly null
delivery `time`.

## Labelless sending codes

POST `/labelless` with a tracking number to obtain a sending code. Optional
`validation.noEdiCheck` defaults to `false`.

GET `/labelless/{trackingNumber}` performs the same lookup by tracking number.
GET `/labelless/shipment/{sendingCode}` resolves a sending code back to
shipment data.

```json
{
  "searchCriteria": { "trackingNumber": "TRACKING_NUMBER" },
  "validation": { "noEdiCheck": false }
}
```

All three operations return `shipments`, an array of objects that each require
`trackingNumber` and `sendingCode`.

## Validation and authentication errors

Request objects declare `additionalProperties: false`; omit undeclared JSON
fields.

API errors require `errorCode`, `message`, and `details`, even when `details`
is null. Error codes are:

- `JSON_DECODE_ERROR`;
- `VALIDATION_ERROR`;
- `INTERNAL_SERVER_ERROR`;
- `CLIENT_ERROR`;
- `UNAUTHORIZED`;
- `FORBIDDEN`;
- `EXPIRED`;
- `INVALID_TOKEN`;
- `UNKNOWN`;
- `MISSING_HEADER`.

Every operation documents `400` validation, `401` authentication, `403`
forbidden, and `500` internal-server responses.

The `401` examples distinguish a missing token as `UNAUTHORIZED`, an expired
token as `EXPIRED`, and an invalid token as `INVALID_TOKEN`. Other
authentication failures use `403` with `FORBIDDEN`.
