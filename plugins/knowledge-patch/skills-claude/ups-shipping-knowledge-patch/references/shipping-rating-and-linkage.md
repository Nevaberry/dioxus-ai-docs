# Shipping, Rating, and Shipment Linkage

## Shipping, Pickup, account, and tracking schema changes

`LabelDelivery_EMail` no longer has:

- `UndeliverableEMailAddress`
- `FromEMailAddress`
- `FromName`
- `Memo`
- `Subject`
- `SubjectCode`

`Master_SoldTo.AttentionName` is no longer required.

Pickup creation adds `Notification`/`PickupCreationRequest_Notification` and
makes `StateProvince` optional.

Open Account adds `RateTypeCode` and `RateConstructCode`.

Track by Reference Number adds `destCountry`, `destZip`, and `shipperNum`.

## Fees and time in transit

### International Processing Fee

Shipping and Rating recognize surcharge code `573` for the International
Process Fee. Rating can return warning `112259` when the fee is added to a
shipment.

### Premier input

Time in Transit requests accept `premierIndicator` to mark a shipment
containing a Premier package.

## Required request data

### Windsor Lane shipping

Shipping supports Northern Ireland-to/from-GB routes where the GB postcode
begins `BT`, plus Northern Ireland-to/from-EU routes.

The update adds `ConsgineeTypevalue` and `ShipmentRiskEnteringEU`. A commercial
invoice is required or the API returns a warning.

### Roadie and RoadieXD

Roadie rating requests require `AddressLine`. Rating versions `2409` or newer
return `Zone`.

Shipping and Rating also add RoadieXD service types, subtypes, accessorials,
and surcharge codes.

### Mexico shipment tax IDs

Shipping requests for Mexico shipments require tax-ID information, matching
the existing requirement for Indonesia and Vietnam.

## Master and child shipment linkage

World Ease master and child shipments must be created with the Shipping API,
including World Ease packages originating in Canada.

Consolidated Worldwide Economy packages are related to their master carton
through `MasterCartonID` for cross-level tracking.
