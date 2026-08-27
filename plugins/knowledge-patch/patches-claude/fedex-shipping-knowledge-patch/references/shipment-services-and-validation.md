# Shipment services and validation

## Shipment email notifications

Ship can send exception and delivery notifications to:

- The recipient.
- As many as six additional email addresses.

## Pickup email notifications

Pickup notifications cover:

- Create or modify confirmation.
- Day-before reminders.
- Morning-of reminders.
- Successful pickup.
- Unsuccessful pickup.

`pickupNotificationDetail\emailDetails\locale` rejects invalid locale values.

## Authenticated Delivery

For eligible U.S. and Canadian shipments, request FedEx Authenticated
Delivery with `FEDEX_AUTHENTICATED_DELIVERY` in
`shipmentSpecialServices.specialServiceType`.

## Sold-to party

The Ship request's `soldTo` object identifies the purchaser when that party
differs from the recipient or importer of record.

## Shipper contact validation

Under `shipper/contacts`, at least one of these values must be present:

- `personName`.
- `companyName`.

Leaving both blank returns an error.

## U.S.-destination C.O.D. retirement

Since July 31, 2023, C.O.D. and E.C.O.D. are unavailable for FedEx Express
and Ground shipments destined for the U.S.

The change does not affect:

- Intra-Canada shipments.
- FedEx Ground U.S.-to-Canada shipments.
- Other supported regions.

## Email return shipment cancellation

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
