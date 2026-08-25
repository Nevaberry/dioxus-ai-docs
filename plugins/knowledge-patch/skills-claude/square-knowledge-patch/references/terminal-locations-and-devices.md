# Terminal, locations, and devices

## Terminal defaults

`PaymentOptions.autocomplete` defaults to `true`.

## Terminal regional capabilities

Linked-order Terminal checkouts expanded to Canada, the UK, and Australia.
Localized order receipts became generally available in Japan and the EU.

Terminal checkout support for the following capabilities expanded to
Australia, Canada, Japan, and the UK:

- App fees
- Delayed capture
- Statement descriptors
- Team-member IDs
- Tip money

The Terminal API can add credit-card surcharges in the US.

## Location address validation

`Location` address fields reject emojis, control characters, and special
symbols.

## Location receipt fields

Beta `Location.custom_receipt_text` and `Location.return_policy` can be read
with `RetrieveLocation` or `ListLocations` and set or cleared with
`UpdateLocation`. Each field is limited to 1,000 characters.

## Devices API hardware details

Devices API adds `DeviceType.HANDHELD` for Square Handheld. It also adds a
`mac_address` field to both `WifiDetails` and `EthernetDetails`.

## GraphQL devices

Square GraphQL adds `devices` for retrieving a seller's POS and peripheral
devices.
