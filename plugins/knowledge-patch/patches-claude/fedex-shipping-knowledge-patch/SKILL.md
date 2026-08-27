---
name: fedex-shipping-knowledge-patch
description: FedEx Shipping
version: null
license: MIT
metadata:
  author: Nevaberry
---


# FedEx Shipping Knowledge Patch

Use this skill when implementing or maintaining FedEx shipping API
integrations involving tracking, rating, pickup, shipment creation, customs,
labels, trade documents, or migration from FedEx Web Services.

## Reference index

| Reference | Topics |
| --- | --- |
| [tracking-and-visibility.md](references/tracking-and-visibility.md) | Account tracking webhooks, Basic Integrated Visibility limits and fields, date-only timestamps |
| [rating-and-pickup.md](references/rating-and-pickup.md) | Hold at Location filtering, One Rate selection, pickup charges, surcharge details, inbound rating rules |
| [shipment-services-and-validation.md](references/shipment-services-and-validation.md) | Notifications, Authenticated Delivery, party validation, C.O.D., email returns, EU domestic services |
| [customs-and-regulatory.md](references/customs-and-regulatory.md) | Commodity regulation, European simplified shipping, Ireland postal codes, Canadian export reporting |
| [labels-and-documents.md](references/labels-and-documents.md) | Thermal labels, German weight icons, encoded trade-document images |
| [migration.md](references/migration.md) | FedEx Web Services maintenance status and API migration |

## Start with retirements and required changes

### Migrate away from FedEx Web Services

FedEx Web Services entered maintenance-only support on July 1, 2026 and is
approaching retirement. Migrate integrations to FedEx APIs instead of
expecting further FedEx Web Services development.

### Do not offer U.S.-destination C.O.D.

Since July 31, 2023, C.O.D. and E.C.O.D. are unavailable for FedEx Express
and Ground shipments destined for the U.S.

This retirement does not affect:

- Intra-Canada shipments.
- FedEx Ground U.S.-to-Canada shipments.
- Other supported regions.

### Require the announced Ireland postal code

Merchant address data for Ireland must account for the announced Eircode
postal-code requirement. Do not treat the postal code as optional.

### Report Canadian exports at the threshold

The Canadian-export announcement requires electronic reporting for goods
valued at CAD 2,000 or more. Customs workflows must not silently omit the
declaration at that threshold.

## Tracking quick reference

### Choose push or pull tracking deliberately

The Tracking Account Number Webhook API pushes near-real-time events for
every shipment associated with a subscribed account, including inbound,
outbound, and third-party-billed shipments. A subscription can send either:

- The full tracking history.
- Only the current event.

It can also push estimated delivery date or time-window changes.

Basic Integrated Visibility, formerly the Track API, is pull-based and is
limited to 100,000 calls per day.

### Read Basic Integrated Visibility fields precisely

| Field | Supported value or location |
| --- | --- |
| `scanEvents.eventType` | `AE` for early; `AO` for on-time |
| `deliveryOptionEligibilityDetails.option` | `DISPUTE_DELIVERY`, `RETURN_TO_SHIPPER`, or `SUPPLEMENT_ADDRESS` |
| Estimated window start | `estimatedDeliveryTimeWindow.window.begins` |
| Estimated window end | `estimatedDeliveryTimeWindow.window.ends` |

### Treat date-only events as UTC midnight

Advanced Integrated Visibility events without a time component use
`00:00:00+00:00`. Interpret that value as UTC midnight, not local time.

## Rating and pickup quick reference

### Pre-validate Hold at Location acceptance

Locations Search can use weight and dimensions alone. It also accepts these
optional inputs when finding a Hold at Location site:

- Total Customs Value.
- Declared Value.
- Package Type.
- Package Count.
- Special Handling.
- Duties and Taxes payor data.

Incomplete pre-validation can select a site that refuses the package or can
cause a Ship API error.

### Select One Rate results

Set optional `rateDisplayOption` to one of:

- `LOWER_RATE`.
- `SELECTED_RATES_INCLUDING_F1R`.
- `SELECTED_RATES_EXCLUDING_F1R`.

`LOWER_RATE` compares One Rate with standard rates. It is also the fallback
when the input is omitted or invalid. With `LOWER_RATE`, omitting dimensions
returns only the customer-supplied-packaging rate.

### Include pickup rates when creating a shipment

Request pickup charges with:

```text
processingOptions=INCLUDE_PICKUPRATES
```

For future-day quotes, also set:

- `pickupDetail.requestType=FUTURE_DAY`.
- `requestedShipment.pickupDetail.readyPickupDateTime`.
- `requestedShipment.pickupDetail.latestPickupDateTime`.

Single on-call pickup rates are charged per stop in the U.S. and Canada,
excluding Puerto Rico and other U.S. territories. Regular automated pickup
charges are weekly and based on selected pickup days.

## Shipment quick reference

### Request Authenticated Delivery

For eligible U.S. and Canadian shipments, put
`FEDEX_AUTHENTICATED_DELIVERY` in
`shipmentSpecialServices.specialServiceType`.

### Validate shipper contacts

Under `shipper/contacts`, at least one of `personName` or `companyName` must
be present. Leaving both blank returns an error.

The Ship request's `soldTo` object identifies the purchaser when the
purchaser differs from the recipient or importer of record.

### Cancel an email return shipment

The Cancel Shipment endpoint requires the following flag to identify and
cancel an email return shipment:

```json
{ "emailreturnshipment": true }
```

## Customs quick reference

### Attach commodity-level regulatory data

Ship accepts a `regulatoryDetails` array alongside customs declarations for
per-commodity compliance data such as CPSC certification. The related
Regulatory API can supply that data.

### Use simplified commodity shipping where applicable

For goods already in free circulation between European countries,
Simplified Commodity Shipping permits a commodity description instead of
full commodity details in the ship request.

## Labels and documents quick reference

### Use current thermal-label capabilities

Ship supports 300 DPI thermal output without a label-format change. It also
accepts these `labelStockType` values:

- `STOCK_4X85_TRAILING_DOC_TAB`.
- `STOCK_4X105_TRAILING_DOC_TAB`.

### Upload encoded trade-document images

The Trade Documents Upload API provides an Upload Encoded Image endpoint for
submitting encoded images.

## Apply the detailed guidance

Open the reference file that matches the integration task. Preserve the
stated eligibility, geography, service, account, and request conditions when
applying any item.
