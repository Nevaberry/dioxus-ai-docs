# International compliance and delivery assurance

## Protected Delivery Token

Protected Delivery Token lets a shipper require a PIN before package release.
It tokenizes the shipper-generated PIN instead of exposing it directly.

## Customs Detail

Customs Detail supplies current UPS-shipment compliance requirements so
integrations can collect more accurate customs data before submission.

## Windsor Lane shipping

Shipping supports Northern Ireland-to/from-GB routes where the GB postcode
begins `BT`, plus Northern Ireland-to/from-EU routes.

The update adds `ConsgineeTypevalue` and `ShipmentRiskEnteringEU`.

A commercial invoice is required or the API returns a warning.

## Mexico shipment tax IDs

Shipping requests for Mexico shipments require tax-ID information. This
matches the existing requirement for Indonesia and Vietnam.

## Global Checkout GraphQL API

Global Checkout provides guaranteed international duty-and-tax quotes at
checkout through a GraphQL API.

Its country, province, and measurement-unit codes are defined in a dedicated
appendix.

## Export Assure

Export Assure provides interactive description-of-goods guidance and
destination-specific commodity compliance checks.

## DeliveryDefense Address Confidence

DeliveryDefense Address Confidence provides a pre-label address-confidence
score based on delivery data.
