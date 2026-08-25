# Trackers and tracking data

## Standalone Tracker creation and identity

For `POST /v2/trackers`, omitting `carrier` invokes auto-detection. Ambiguous
tracking codes can match multiple carriers, and selecting the carrier
explicitly is faster. Some carriers require carrier-specific credentials for
third-party tracking.

Trackers are immutable. When the same user creates the same `tracking_code`
and `carrier` within three months, EasyPost returns the original Tracker rather
than a duplicate.

`POST /v2/trackers/batch` creates up to 100 Trackers from tracking codes in one
request.

## Status and event details

The current Tracker `status` is one of:

- `unknown`
- `pre_transit`
- `in_transit`
- `out_for_delivery`
- `delivered`
- `available_for_pickup`
- `return_to_sender`
- `failure`
- `cancelled`
- `error`

`status_detail` further distinguishes conditions including address correction,
facility arrival and departure, damage, delay, delivery exceptions,
expiration, holds, loss, missorting, refusal, transfer to a destination
carrier, transit exceptions, and weather delay.

Historical scans are stored in `tracking_details`. Scan timestamps use a local
zone inferred from a sufficiently complete `tracking_location`; otherwise they
use UTC.

`carrier_detail` can expose local delivery estimates, structured origin and
destination locations, a guaranteed date, an asynchronously populated
`alternate_identifier` for hybrid services, and `initial_delivery_attempt`.

Tracking responses can include the carrier code. Geocoded events can include a
local timestamp and confidence score. FedEx Tracking API results can expose
signature images and proof-of-delivery documents.

## Carrier API strings

The `carrier` value is an API tracking string and is not always the display
name.

| Display name | API string |
| --- | --- |
| CDL Last Mile Solutions | `ColumbusLastMile` |
| DHL eCommerce Solutions | `DhlEcs` |
| LaserShip | `LaserShipV2` |
| Passport | `PassportGlobal` |
| TForce Logistics | `TforceConcise` |
| USPS Ship | `UspsShip` |

## Deterministic test-mode states

These test-mode codes create canned carrier-like tracking data and send an
Event to a test-mode webhook URL.

| Tracking code | Status |
| --- | --- |
| `EZ1000000001` | `pre_transit` |
| `EZ2000000002` | `in_transit` |
| `EZ3000000003` | `out_for_delivery` |
| `EZ4000000004` | `delivered` |
| `EZ5000000005` | `return_to_sender` |
| `EZ6000000006` | `failure` |
| `EZ7000000007` | `unknown` |

## Lookup and list windows

Find Trackers by code with `GET /v2/trackers` and the plural
`tracking_codes` array, optionally narrowed by `carrier`.
`GET /v2/trackers/:id` accepts only a Tracker ID.

The list defaults to records from one month ago through the end of the current
day. If only one datetime bound is supplied, it defaults to a one-month span
around that bound. Older matches require an explicit `start_datetime`.
`page_size` defaults to 20 and caps at 100.

## Permanent deletion

`DELETE /v2/trackers/:id` permanently removes a Tracker, stops all future
webhook Event deliveries for it, and makes subsequent retrieval return
`404 Not Found`.

```json
{"success": true}
```
