# Rating, Pickups, and Locations

## Hold at Location acceptance filtering

Locations Search accepts these optional inputs in addition to weight and
dimensions when finding a Hold at Location site:

- Total Customs Value.
- Declared Value.
- Package Type.
- Package Count.
- Special Handling.
- Duties and Taxes payor data.

Weight and dimensions alone still work. Incomplete pre-validation can select a
site that refuses the package or causes a Ship API error.

## Selecting One Rate results

Optional `rateDisplayOption` accepts:

- `LOWER_RATE`, which compares One Rate with standard rates.
- `SELECTED_RATES_INCLUDING_F1R`.
- `SELECTED_RATES_EXCLUDING_F1R`.

`LOWER_RATE` is also the fallback for omitted or invalid input. With
`LOWER_RATE`, omitting dimensions returns only the
customer-supplied-packaging rate.

## Extra Small One Rate packaging

`FEDEX_EXTRA_SMALL_BOX` is available to enabled accounts in both Comprehensive
Rates and Ship for FedEx Express One Rate. It requires FedEx-provided packaging
and has the same 50 lb maximum as the other One Rate packages.

## Pickup charges during shipment creation

Single on-call pickup rates are charged per stop in the U.S. and Canada,
excluding Puerto Rico and other U.S. territories. Regular automated pickup
charges are weekly and based on selected pickup days.

Request pickup charges with:

```text
processingOptions=INCLUDE_PICKUPRATES
```

Future-day quotes also require:

```text
pickupDetail.requestType=FUTURE_DAY
requestedShipment.pickupDetail.readyPickupDateTime
requestedShipment.pickupDetail.latestPickupDateTime
```

## Package-level surcharge details

For supported multipiece and consolidation services, applicable rate and ship
responses expose these package-level charges alongside aggregate shipment
charges:

- AHS Packaging.
- AHS Dimension.
- AHS Weight.
- Oversize.
- AHS Freight Dimension.
- Non-Stackable.

Non-U.S. High Density, Enhanced Security, and Single Piece surcharges remain
shipment-level charges.

## U.S. inbound and handling rating rules

The U.S. Inbound Processing Fee applies to inbound international Express and
Ground shipments, except:

- Puerto Rico-to-U.S. shipments.
- U.S.-to-Puerto Rico shipments.
- U.S.-origin shipments.

Packages subject to Additional Handling Surcharge—Dimension have a 40 lb
(18 kg) minimum billable weight.
