---
name: easypost-knowledge-patch
description: EasyPost
version: null
license: MIT
metadata:
  author: Nevaberry
---


# EasyPost Knowledge Patch

Use this skill when implementing or reviewing EasyPost integrations involving
addresses, trackers, shipments, labels, rating, carrier accounts, webhooks, or
SDK and API compatibility.

## Reference index

| Reference | Topics |
| --- | --- |
| [addresses.md](references/addresses.md) | Address verification triggers, carrier verification, existing-address verification, and line normalization |
| [tracking.md](references/tracking.md) | Tracker states, scan details, identity, carrier strings, test data, lookup, deletion, and batch creation |
| [shipments-and-rating.md](references/shipments-and-rating.md) | Shipment creation and purchase, labels, listing, claims, rate adjustments, international rating, and carrier options |
| [platform-and-sdks.md](references/platform-and-sdks.md) | SDK compatibility, generic requests, webhooks, throttling, carrier accounts, groups, sessions, and subscriptions |

## Critical compatibility changes

### Address verification is presence-based

On `POST /v2/addresses`, including either `verify` or `verify_strict` triggers
delivery and ZIP verification even if the key's value is `false`. Omit both
keys when verification is not wanted.

`verify` returns the Address with per-check results. `verify_strict` takes
precedence and returns an error when the address is unverified; correctable
addresses are corrected and returned.

```json
{
  "address": {
    "street1": "417 Montgomery St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94104",
    "country": "US"
  },
  "verify_strict": true
}
```

### Shipment creation is immutable

`POST /v2/shipments` creates an immutable Shipment. Supply all inputs up
front. Valid `to_address`, `from_address`, and `parcel` values automatically
populate `rates`.

Addresses and parcels may be existing IDs or inline objects.
`customs_info` is required for international destinations, including US
territories. If `return_address` is omitted, it defaults to `from_address`.
`carrier_accounts` limits rating, but any invalid or disabled supplied account
causes an error.

V2 shipment validation rejects missing or zero-valued parcel details.

```json
{
  "shipment": {
    "to_address": {"id": "adr_..."},
    "from_address": {"id": "adr_..."},
    "parcel": {"id": "prcl_..."},
    "carrier_accounts": ["ca_..."]
  }
}
```

### Node.js SDK behavior changed

The Node.js SDK:

- Uses `fetch` instead of `superagent`.
- Drops Node 16 support.
- Renames `superagentMiddleware` to `httpMiddleware`.
- Renames `fetchClient` to `httpClient`.
- Returns API resources as plain JSON-compatible objects rather than
  model-class instances.

### Index endpoints are rate-limited

Index endpoints have request-per-second rate limiting. Integrations that
enumerate resources must tolerate throttling instead of assuming unrestricted
pagination.

### Shipment references are not unique

`GET /v2/shipments/:id` accepts either an EasyPost Shipment ID or a
caller-supplied `reference`. Reference uniqueness is not enforced, so use the
generated ID for reliable retrieval.

## Common operations

### Use carrier-grade address verification

Set `verify_carrier` to `ups` or `fedex` alongside `verify` or
`verify_strict`. This uses the selected carrier's Address Verification Service
instead of standard EasyPost verification. The response `verifications`
object includes a `verify_carrier` key naming the service used.

```json
{"verify": true, "verify_carrier": "fedex"}
```

### Verify an existing Address

An existing Address is immutable. Verify it with
`GET /v2/addresses/:id/verify`. The response wraps the normalized replacement
in `address`.

The replacement's `verifications.zip4` and `verifications.delivery` entries
contain `success`, field errors, and details. Delivery details can include
latitude, longitude, and an IANA time zone.

### Buy a rated Shipment

Purchase with `POST /v2/shipments/:id/buy` and a `rate.id`. The response fills
`tracking_code` and `postage_label`. Optional `insurance` must be a USD string.
Labels default to PNG unless `options.label_format` requests another format.

```json
{"rate": {"id": "rate_..."}, "insurance": "249.99"}
```

### Use one-call shipment purchase

When the carrier service is already known, include both `service` and
`carrier_accounts` in the `POST /v2/shipments` payload to collapse the normal
create-then-buy flow.

```json
{
  "shipment": {
    "to_address": {"id": "adr_..."},
    "from_address": {"id": "adr_..."},
    "parcel": {"id": "prcl_..."},
    "service": "NextDayAir",
    "carrier_accounts": ["ca_..."]
  }
}
```

### Convert a purchased label

Use `GET /v2/shipments/:id/label?file_format=ZPL` to convert a purchased
Shipment label to `PDF`, `ZPL`, or `EPL2`. The original label must be PNG.
Conversion works best from a 4x6 PNG to ZPL.

### Create and identify Trackers

For `POST /v2/trackers`, omitting `carrier` invokes auto-detection. Ambiguous
codes can match multiple carriers, explicit selection is faster, and some
carriers require carrier-specific credentials for third-party tracking.

Trackers are immutable. When the same user creates the same `tracking_code`
and `carrier` within three months, EasyPost returns the original Tracker
instead of a duplicate.

The `carrier` field uses an API tracking string, which may differ from the
display name. See [tracking.md](references/tracking.md) for non-obvious
mappings.

### Query Trackers correctly

Use `GET /v2/trackers` with the plural `tracking_codes` array, optionally
narrowed by `carrier`, to find Trackers by code. `GET /v2/trackers/:id`
accepts only a Tracker ID.

The list defaults to one month ago through the end of the current day. With
only one datetime bound, it uses a one-month span around that bound. Supply an
explicit `start_datetime` for older matches. `page_size` defaults to 20 and
has a maximum of 100.

### Delete Trackers with care

`DELETE /v2/trackers/:id` permanently removes the Tracker, stops all future
webhook Event deliveries for it, and makes later retrieval return
`404 Not Found`.

```json
{"success": true}
```

### Use generic SDK requests when needed

The C#, Java, Node.js, PHP, and Ruby SDKs expose a generic request interface
for arbitrary API endpoints, including endpoints without typed resource
wrappers.

## Additional routing

- For status values, event fields, deterministic test codes, and carrier API
  strings, read [tracking.md](references/tracking.md).
- For request-only claim data, shipment-list cursor rules, rating systems,
  insurance, and carrier-specific delivery behavior, read
  [shipments-and-rating.md](references/shipments-and-rating.md).
- For webhook events, account lifecycle, groups, JWT sessions, and
  subscriptions, read [platform-and-sdks.md](references/platform-and-sdks.md).
