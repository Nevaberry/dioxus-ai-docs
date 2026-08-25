# Posti Tracking API v7

## Base URL and authentication

The Tracking REST API uses:

```text
https://api.posti.fi/tracking/7
```

Every operation inherits an OAuth 2.0 client-credentials scheme whose token
URL is `/tracking/oauth/token`. Use the resulting bearer token with ordinary
JSON or `application/vnd.tracking.api.v1+json` responses.

```http
GET /tracking/7/shipments/trackingnumber/TRACKING_NUMBER HTTP/1.1
Host: api.posti.fi
Authorization: Bearer ACCESS_TOKEN
Accept: application/json
```

## Dedicated shipment lookup aliases

All shipment searches return the same response envelope. Dedicated paths map
to generic find keys as follows:

| Dedicated path | Find behavior |
| --- | --- |
| `waybillnumber/{waybillNumber}` | `freight_waybill_number` |
| `trackingnumber/{trackingNumber}` | Parcel and freight tracking numbers |
| `trackingnumbers/{trackingNumbers}` | Comma-separated values; parcel and freight tracking numbers |
| Sender-reference path | Corresponding parcel and freight sender-reference keys |
| Receiver-reference path | Corresponding parcel and freight receiver-reference keys |
| Order-number path | Corresponding parcel and freight order-number keys |
| `consignmentnumber` | Parcel-only |
| `errandcode` | Parcel-only |
| `goodsitemid/{goodsItemId}` | Documented as an alias for `freight_tracking_number` |

Most single lookup values must be 3–60 characters.
`phonenumber/{phoneNumber}` is restricted, accepts 7–30 characters, and has a
`direction` of `RECEIVING`, `SENDING`, or `BOTH`, with `BOTH` as the default.

## Generic find selectors

Use GET `/tracking/7/shipments/find` with a required `keywords` array of 1–100
unique strings. Use `/tracking/7/shipments/find/{keyword}` for one
3–60-character value.

`keys` defaults to `all`. It accepts comma-separated groups or keys with `!`
negation:

- `parcel_all`;
- `freight_all`;
- parcel tracking, consignment, errand, order, receiver-reference, and
  sender-reference keys;
- freight waybill, tracking, order, receiver-reference, and sender-reference
  keys;
- `mps_cod_group`;
- `delivery_group`.

The path form also documents `sequence`.

```http
GET /tracking/7/shipments/find/ORDER-123?keys=all,!parcel_order_number&type=FREIGHT HTTP/1.1
Host: api.posti.fi
Authorization: Bearer ACCESS_TOKEN
```

The OpenAPI schema encodes the whole `keys` choice list as one enum string
rather than separate enum values. The path form also contains a malformed
`!delivery_groupsequence` entry. Generated clients may need this parameter
corrected to behave as the prose contract describes.

## Search filters and pagination

Every shipment search supports:

- `lastModified` as an ISO 8601 lower bound;
- `type=ANY|FREIGHT|PARCEL`;
- `order=ASC|DESC`;
- `lengthUnit`, `massUnit`, and `volumeUnit` response-unit selectors;
- `combined`;
- `start`;
- `limit`.

`combined=true` asks the service to merge logically identical shipments, but
it is typed as a string and is explicitly warned not to work reliably with
pagination.

`start` defaults to `0`. `limit` defaults to `100` and is schema-bounded to
1–1000, while the operation text separately warns of a hard 100-shipment
return limit. Examples use `start=0&limit=10` followed by
`start=10&limit=20`. Follow returned counts and test paging semantics rather
than treating the schema maximum as the page size.

## Event-date search

Restricted GET `/tracking/7/shipments/event/date` finds shipments having
events in a date-time interval. `from` is inclusive, `to` is exclusive, and
both are optional. The normal shipment-search filters and pagination
parameters also apply.

## Shipment response envelope

`SearchResponseDto` has independent `freightShipments` and `parcelShipments`
arrays. None of the 48 component schemas declares required properties, so
consumers must tolerate absent fields.

### Parcel shipments

Parcel results expose:

- tracking and consignment identifiers;
- product and services;
- locations;
- parties and references;
- quantities;
- events;
- delivery estimates;
- pickup and service-point data;
- monetary and customs data;
- status.

Parcel status codes are:

- `WAITING`;
- `RECEIVED`;
- `IN_TRANSPORT`;
- `READY_FOR_PICKUP`;
- `DELIVERED`;
- `RETURNED_TO_SENDER`;
- `OUT_FOR_DELIVERY`;
- `RETURN_WAITING`;
- `RETURN_IN_TRANSPORT`;
- `RETURN_READY_FOR_PICKUP`;
- `RETURN_DELIVERED`;
- `CUSTOMS`.

Expedition types are `NORMAL`, `DELIVERY_OFFICE_RETURN`, `CUSTOMER_RETURN`,
`FORWARDING`, `ARCHIVING`, and `NEARBY_LOCKER_RETURN`.

### Freight shipments

Freight results expose the waybill, product and services, pickup and delivery
ranges, locations and parties, references, totals, goods items and their
packages, events, COD, and status.

Freight status codes are `ORDER_RECEIVED`, `IN_TRANSPORT`, `IN_DELIVERY`, and
`DELIVERED`.

## Events and localization

Parcel, freight, and freight-package events share:

- event, reason, and action codes;
- localized names and descriptions;
- timestamp;
- location;
- recipient signature;
- optional extra information.

Parcel events additionally carry country-location, locker and shelf data,
manual-handling metadata, organization data, delivery-office type, and
reservation code.

Localized strings may contain `fi`, `en`, `sv`, `et`, `lt`, `lv`, and `ru`
values.

## Quantity selectors and returned units

Query selectors use these long values:

| Quantity | Query values |
| --- | --- |
| Length | `MILLIMETRE`, `CENTIMETRE`, `METRE` |
| Mass | `GRAM`, `KILOGRAM` |
| Volume | `CUBIC_MILLIMETRE`, `CUBIC_CENTIMETRE`, `CUBIC_DECIMETRE`, `LITRE`, `CUBIC_METRE` |

Returned quantity objects use:

| Quantity | Returned units |
| --- | --- |
| Length | `mm`, `cm`, `m` |
| Mass | `g`, `kg` |
| Volume | `mm3`, `cm3`, `dm3`, `l`, `m3` |

## Reservation-status statistics

Restricted GET `/tracking/7/reservations/status` requires:

- delivery-window `from` and `to` date-times;
- destination `country`;
- a `postcode` array.

Optional `product` and `service` arrays filter product and additional-service
groups. A product value such as `2182:3122` means product 2182 with additional
service 3122.

The response contains `reservations`; each has `from`, `to`, `count`, and
`trackingNumbers`.

The array schemas do not specify custom serialization, while their examples
are comma-separated strings such as `02100,02110,02140`. Verify serialization
when bypassing a generated client.

## Response declaration caveat

The specification declares `400`, `401`, `403`, `404`, `408`, `500`, and `502`
responses without bodies. It places the typed success payload only under
`default` rather than an explicit 2xx response.

Client generators that type responses by status code may therefore need an
override for `SearchResponseDto` or `ReservationStatusesResponseDto`.
