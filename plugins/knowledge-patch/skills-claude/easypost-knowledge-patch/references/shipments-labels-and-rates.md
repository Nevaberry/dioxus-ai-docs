# Shipments, labels, rates, and claims

## Immutable Shipment creation and rating

`POST /v2/shipments` creates an immutable Shipment, so supply all inputs up
front. Valid `to_address`, `from_address`, and `parcel` values automatically
populate `rates`; addresses and parcels may be existing IDs or inline objects.

`customs_info` is required for international destinations, including US
territories. An omitted `return_address` defaults to `from_address`.

Supplying `carrier_accounts` limits rating. If any supplied carrier account is
invalid or disabled, the request errors.

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

Create Shipment also accepts `return_address`. V2 shipment validation rejects
missing or zero-valued parcel details.

## Request-only claim line items

Shipment `line_items` support carrier-claim automation, but are not passed to
the carrier and are not returned in the response. Each item requires
`total_line_value` as a USD string and an `item_description`.

```json
{
  "line_items": [
    {"total_line_value": "125.00", "item_description": "Camera"}
  ]
}
```

## Buying a rated Shipment

Purchase a rate through `POST /v2/shipments/:id/buy` by supplying a `rate.id`.
The response fills `tracking_code` and `postage_label`.

Optional `insurance` must be a USD string. Labels default to PNG unless the
Shipment's `options.label_format` requests a different format.

```json
{"rate": {"id": "rate_..."}, "insurance": "249.99"}
```

## One-call purchase

When the carrier service is already known, collapse the create-then-buy flow
into `POST /v2/shipments` by including both `service` and `carrier_accounts` in
the Shipment payload.

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

## Listing and retrieving Shipments

`GET /v2/shipments` defaults to purchased Shipments from one month ago through
the end of the current day. It also defaults to `include_children=false` and a
page size of 20; the maximum page size is 100.

`before_id` and `after_id` are mutually exclusive. If only one datetime bound
is supplied, the list uses a one-month window around it. `has_more` indicates
another page.

`GET /v2/shipments/:id` accepts either the EasyPost Shipment ID or the
caller-supplied `reference`. Reference uniqueness is not enforced, so use the
generated ID for reliable retrieval.

## Label requests and conversion

REST-label requests support shipment- and package-level descriptions,
delivery-confirmation options, and alternate delivery addresses.

For a purchased Shipment, this endpoint converts a label to `PDF`, `ZPL`, or
`EPL2`:

```text
GET /v2/shipments/:id/label?file_format=ZPL
```

The original label must be PNG. Conversion works best for 4x6 PNG labels
converted to ZPL.

## Rate adjustments and Luma rulesets

Rate-adjustment support applies to shipment creation, rerating, stateless
rating, order creation, and label purchase. Beta availability lookup covers
parent and child accounts.

APIs can manage single or cumulative rulesets. Beta Luma ruleset endpoints
expose adjusted rates in one-call-buy, promise, and buy operations. Ruleset
payload casing is standardized.

## International rating

SmartRate supports international shipments through the Precision Shipping,
Rateless, and Standalone APIs. Public Zonos Landed Cost endpoints provide
international duty-and-tax estimates and guarantees.

## Claims and insurance

Carrier claims accept `line_items`. The minimum included insurance increased
from $50 to $100.

Applicable BuySafe mailed-check claims no longer require `payout_recipient`.
Applicable BuySafe package-protection claims can be filed without EasyPost
evidence attachments.

## Carrier-specific delivery and shipment rules

- Australia Post Safe Drop requires Signature confirmation through a
  carrier-specific delivery-confirmation option.
- Canada Post permits US-to-Canada shipments when Zonos credentials are
  supplied.
- DoorDash supports signature confirmation.
- UPS supports the Additional Handling Indicator, Ground Saver delivery to PO
  boxes, and return-merchandise workflows with QR-code labels.
- DHL Express shipment requests can include importer registration numbers.
