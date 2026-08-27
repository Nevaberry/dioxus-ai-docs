---
name: fedex-shipping-knowledge-patch
description: FedEx Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# FedEx Shipping Knowledge Patch

Use this skill when implementing or reviewing FedEx shipping integrations that
touch tracking, rating, pickup charges, shipment creation, special services,
customs, labels, trade documents, or migration from FedEx Web Services.

## Reference index

| Reference | Topics |
| --- | --- |
| [tracking-and-notifications.md](references/tracking-and-notifications.md) | Account webhooks, Basic Integrated Visibility, timestamps, and email notifications |
| [rating-pickups-and-locations.md](references/rating-pickups-and-locations.md) | Hold at Location filtering, One Rate, pickup charges, surcharges, and U.S. rating rules |
| [shipments-and-services.md](references/shipments-and-services.md) | Shipment fields, Authenticated Delivery, C.O.D., email returns, and EU services |
| [customs-and-trade.md](references/customs-and-trade.md) | Regulatory data, European commodity shipping, trade-document images, and export/address requirements |
| [labels-and-migration.md](references/labels-and-migration.md) | Thermal labels, German handling icons, and Web Services migration |

## Critical compatibility changes

### Migrate away from FedEx Web Services

FedEx Web Services entered maintenance-only support on July 1, 2026 and is
approaching retirement. Migrate integrations to FedEx APIs instead of expecting
further Web Services development.

See [labels-and-migration.md](references/labels-and-migration.md).

### Do not offer retired U.S.-destination C.O.D.

Since July 31, 2023, C.O.D. and E.C.O.D. are unavailable for FedEx Express and
Ground shipments destined for the U.S.

The retirement does not affect:

- Intra-Canada shipments.
- FedEx Ground U.S.-to-Canada shipments.
- Other supported regions.

See [shipments-and-services.md](references/shipments-and-services.md).

### Enforce the Canadian export-reporting threshold

For Canadian exports, electronic reporting is required for goods valued at CAD
2,000 or more. Customs workflows must not silently omit the declaration at that
threshold.

See [customs-and-trade.md](references/customs-and-trade.md).

### Treat date-only webhook timestamps as UTC

Advanced Integrated Visibility events without a time component use
`00:00:00+00:00`. Interpret that value as UTC midnight, not local time.

See [tracking-and-notifications.md](references/tracking-and-notifications.md).

## Rating and pickup quick reference

### One Rate result selection

`rateDisplayOption` accepts:

- `LOWER_RATE`.
- `SELECTED_RATES_INCLUDING_F1R`.
- `SELECTED_RATES_EXCLUDING_F1R`.

`LOWER_RATE` compares One Rate with standard rates. It is also the fallback
when the input is omitted or invalid. With `LOWER_RATE`, omitting dimensions
returns only the customer-supplied-packaging rate.

### Request pickup charges with the required fields

Set:

```text
processingOptions=INCLUDE_PICKUPRATES
```

For a future-day quote, also set:

```text
pickupDetail.requestType=FUTURE_DAY
requestedShipment.pickupDetail.readyPickupDateTime
requestedShipment.pickupDetail.latestPickupDateTime
```

Single on-call pickup rates are charged per stop in the U.S. and Canada,
excluding Puerto Rico and other U.S. territories. Regular automated pickup
charges are weekly and based on the selected pickup days.

### Pre-validate Hold at Location acceptance

Locations Search can accept these optional inputs in addition to weight and
dimensions:

- Total Customs Value.
- Declared Value.
- Package Type.
- Package Count.
- Special Handling.
- Duties and Taxes payor data.

Weight and dimensions alone still work. Incomplete pre-validation can select a
site that refuses the package or causes a Ship API error.

See [rating-pickups-and-locations.md](references/rating-pickups-and-locations.md)
for packaging, surcharge, and inbound-rating details.

## Shipment quick reference

### Validate party and contact fields

Use `soldTo` to identify the purchaser when that party differs from the
recipient or importer of record.

Under `shipper/contacts`, provide at least one of `personName` or `companyName`.
Leaving both blank returns an error.

### Request Authenticated Delivery

For eligible U.S. and Canadian shipments, place
`FEDEX_AUTHENTICATED_DELIVERY` in
`shipmentSpecialServices.specialServiceType`.

### Cancel an email return shipment

The Cancel Shipment endpoint requires `emailreturnshipment: true` to identify
and cancel an email return shipment.

```json
{ "emailreturnshipment": true }
```

See [shipments-and-services.md](references/shipments-and-services.md) for the
complete service and shipment-field guidance.

## Tracking quick reference

### Push and pull tracking

The Tracking Account Number Webhook API pushes near-real-time events for every
shipment associated with a subscribed account, including inbound, outbound,
and third-party-billed shipments. A subscription can send either the full
tracking history or only the current event and can push estimated-delivery date
or time-window changes.

Basic Integrated Visibility, formerly the Track API, is pull-based and limited
to 100,000 calls per day.

### Read the current response fields

- `scanEvents.eventType` can report `AE` for early or `AO` for on-time.
- `deliveryOptionEligibilityDetails.option` can include
  `DISPUTE_DELIVERY`, `RETURN_TO_SHIPPER`, or `SUPPLEMENT_ADDRESS`.
- The estimated window is under
  `estimatedDeliveryTimeWindow.window.begins` and
  `estimatedDeliveryTimeWindow.window.ends`.

See [tracking-and-notifications.md](references/tracking-and-notifications.md) for
notification-recipient and locale behavior.

## Customs and international quick reference

### Attach per-commodity regulatory data

Ship accepts a `regulatoryDetails` array alongside customs declarations for
per-commodity compliance data such as CPSC certification. The related
Regulatory API can supply that data.

### Apply destination and regional requirements

- Merchant address data for Ireland must account for the announced Eircode
  postal-code requirement instead of treating postal code as optional.
- For goods already in free circulation between European countries,
  Simplified Commodity Shipping permits a commodity description instead of
  full commodity details in the ship request.
- Ship supports the EU domestic services FedEx First, Priority Express,
  Priority, Priority Express Freight, and Priority Freight.

See [customs-and-trade.md](references/customs-and-trade.md) for trade-document
upload and reporting details.

## Label quick reference

Ship supports 300 DPI thermal output without a label-format change. It also
accepts these `labelStockType` values:

- `STOCK_4X85_TRAILING_DOC_TAB`
- `STOCK_4X105_TRAILING_DOC_TAB`

For inbound-to-Germany and domestic German parcel and freight shipments,
labels automatically include 10+ kg or 20+ kg handling icons. This applies to
every automated label channel and replaces the former manual-sticker
workaround.

See [labels-and-migration.md](references/labels-and-migration.md).
