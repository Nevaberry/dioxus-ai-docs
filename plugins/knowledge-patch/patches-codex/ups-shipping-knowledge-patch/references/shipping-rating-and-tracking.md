# Shipping, rating, and tracking

## Expanded error-code surface

Shipping exposes these Label Recovery codes:

- `9801061`
- `9801062`
- `9801064`
- `9801065`
- `9801067`

Shipping also exposes `120466`, and the description of `120200` changed.

Dangerous Goods adds `9190048`. Pre Notification adds `9290059`.

Error handlers must accept all of these as known UPS codes.

## International Process Fee

Shipping and Rating recognize surcharge code `573` for the International
Process Fee.

Rating can return warning `112259` when the fee is added to a shipment.

## Premier packages in Time in Transit

Time in Transit requests accept `premierIndicator` to mark a shipment
containing a Premier package.

## Delivery Intercept eligibility

Delivery Intercept supports automated intercept requests. Its eligibility
endpoint lets an application determine which intercept type is valid before
submitting a request.

The API can be added through the standard application add/edit flow.

## Roadie and RoadieXD

Roadie rating requests require `AddressLine`.

Rating versions `2409` or newer return `Zone`.

Shipping and Rating add RoadieXD service types, subtypes, accessorials, and
surcharge codes.

## World Ease shipments

World Ease master and child shipments must be created with the Shipping API.
This includes World Ease packages originating in Canada.

## Worldwide Economy master-carton linkage

Consolidated Worldwide Economy packages are related to their master carton
through `MasterCartonID` for cross-level tracking.
