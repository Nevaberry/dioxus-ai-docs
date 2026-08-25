# Matkahuolto Tracking

## Storefront display

Matkahuolto tracking data can be displayed directly in an online store in
addition to the recipient-facing Track & Trace service.

## Tracking query

GET the following endpoint with HTTP Basic authentication:

```text
https://extservices.matkahuolto.fi/mpaketti/public/tracking
```

The test host is `extservicestest.matkahuolto.fi`. `ids` is a comma-separated
list of at most ten shipment or parcel IDs. `from` and `to` use date-time
values such as `2018-01-11T11:47:30`. Supply IDs or time-range input.

```http
GET /mpaketti/public/tracking?ids=MH302164795FI&from=2018-01-11T11:47:30&to=2018-01-11T13:47:30
Accept: application/json
```

XML is the default response. `Accept: application/json` selects JSON.

## Event codes

| Code | Event |
| --- | --- |
| `02` | Advance notice |
| `08` | Picked up from sender |
| `10` | Received at departing parcel point |
| `12` | Consolidated |
| `15` | Received for carriage |
| `25` | Loaded for main transport |
| `35` | Received at destination terminal |
| `40` | Waiting for delivery loading |
| `41` | Waiting for parcel-point loading |
| `45` | Loaded for delivery |
| `46` | Loaded for parcel-point delivery |
| `47` | Delivered to parcel point |
| `48` | Received at parcel point |
| `50` | Ready for collection |
| `55` | First notification |
| `56` | Second notification |
| `57` | Manual notification |
| `60` | Handed to recipient |
| `61` | Handed to proxy |
| `62` | Handover cancelled |
| `65` | COD paid to sender |
| `70` | Returned uncollected |
| `97` | Unsuccessful delivery attempt |
| `104` | Deviation added |

## Event fields and conditional data

Each event contains `EventId`, shipment and parcel numbers, sender reference,
code, timestamp, place, office code, and remarks.

`Signature` appears only for codes `60` and `61`. `ReturnShipmentNumber`
appears only for code `70`.

A valid query with no matching events returns an empty message rather than an
error.

## Tracking errors

Tracking errors combine HTTP status with an application code:

| HTTP/application code | Meaning |
| --- | --- |
| `400/10` | Missing parameter |
| `400/11` | Invalid date |
| `400/12` | More than ten IDs |
| `400/13` | Excessive time range |
| `401/50` | Authentication failure |
| `405/60` | Non-GET method |

XML error payloads use an `Error` group containing `EventId`, `ErrorCode`, and
`ErrorText`.
