# Shipments and Services

## Authenticated Delivery

For eligible U.S. and Canadian shipments, request FedEx Authenticated Delivery
with `FEDEX_AUTHENTICATED_DELIVERY` in
`shipmentSpecialServices.specialServiceType`.

## Sold-to party

The Ship request's `soldTo` object identifies the purchaser when that party
differs from the recipient or importer of record.

## Shipper contact validation

Under `shipper/contacts`, at least one of `personName` or `companyName` must be
present. Leaving both blank returns an error.

## U.S.-destination C.O.D. retirement

Since July 31, 2023, C.O.D. and E.C.O.D. are unavailable for FedEx Express and
Ground shipments destined for the U.S.

The following are unaffected:

- Intra-Canada shipments.
- FedEx Ground U.S.-to-Canada shipments.
- Other supported regions.

## Cancelling an email return shipment

The Cancel Shipment endpoint requires `emailreturnshipment: true` to identify
and cancel an email return shipment.

```json
{ "emailreturnshipment": true }
```

## EU domestic services

The Ship API supports these EU domestic services:

- FedEx First.
- Priority Express.
- Priority.
- Priority Express Freight.
- Priority Freight.
